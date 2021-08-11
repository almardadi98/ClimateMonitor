from influxdb import InfluxDBClient
from w1thermsensor import W1ThermSensor
import RPi.GPIO as GPIO
import raspberry_am2320 as AOSONG
import logging
import time
import socket

logging.basicConfig(filename='voktun_service.log',format='%(asctime)s %(message)s',level=logging.INFO)
logging.debug('Starting script')


class ClimateData:
    def __init__(self, location, hostname):
        self.location = location
        self.hostname = hostname
        self.temperature = -1.0
        self.humidity = -1.0

    def __repr__(self):
        return f'{self.hostname!r}@{self.location!r} | Temperature: {self.temperature!r}°C, Humidity: {self.humidity!r}%'

    def set_temperature(self, temperature):
        self.temperature = temperature
    
    def set_humidity(self, humidity):
        self.humidity = humidity

    def get_temperature(self):
        return self.temperature

    def get_humidity(self):
        return self.humidity

    def get_climate_in_json(self):
        assert self.temperature != None
        assert self.humidity != None

        self.json_body = [
            {
                "measurement": "Climate",
                "tags": {
                    "host": self.hostname,
                    "Location": self.location,
                },
                "fields": {
                    "Temperature": self.temperature,
                    "Humidity": self.humidity,
                }
            }
        ]
        return self.json_body



def main():
    hostname = socket.gethostname()

    #Hitaskynjari
    try:
        temperature_sensor = W1ThermSensor()
    except:
        temperature_sensor = None

    #Rakaskynjari (og hita en er ekki notaður sem slíkur)
    # initialize GPIO
    GPIO.setmode(GPIO.BCM)
    # read data using pin 17
    sensor = AOSONG.AM2320_1WIRE(pin=17)


    InfluxServer = 'exampleserver'
    
    logging.debug('InfluxDB server: ' + InfluxServer)
    #Búa til climatedata objectið
    climate = ClimateData("Skrifstofa", hostname)

    client = InfluxDBClient(InfluxServer, 8086, 'InfluxUser', 'InfluxPassword', 'InfluxDatabase')

    while True:
        print(climate)

        try:
            #Ekki spyrja oftar en á tveggja sek fresti!
            (temperature_am2320,humidity) = sensor.readSensor()
            climate.set_humidity( humidity ) 

        except AOSONG.DataError as e:
            #Try try again
            logging.debug(f"AM2320 read error: {e}")

        #Bara reyna að skrá hitastig ef það er hitaskynjari tengdur
        if temperature_sensor:
            climate.set_temperature( temperature_sensor.get_temperature() )

        try:
            json_climate_data = climate.get_climate_in_json()
            logging.debug(climate)
            logging.debug("Sending json data...")
            client.write_points(json_climate_data)
        except IOError:
            logging.debug("IO error, check connection to database")
        except Exception as e:
            logging.debug(f"Error occured: {e}")
        time.sleep(5)


if __name__ =='__main__':
    main()

GPIO.cleanup()