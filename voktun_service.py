from datetime import datetime
from os import read
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
from climate import Climate
from w1thermsensor import W1ThermSensor
import RPi.GPIO as GPIO
import raspberry_am2320 as AOSONG
import logging
import time
import socket
import json

from influx_settings import InfluxSettings

logging.basicConfig(filename='voktun_service.log',
                    format='%(asctime)s %(message)s', level=logging.INFO)
logging.debug('Starting script')


def read_settings(filename: str) -> InfluxSettings:
    with open(filename, "r", encoding="UTF-8") as file:
        settings_dict = json.load(file)
    return InfluxSettings(**settings_dict)


def write_climate_data(climate_data: Climate, settings: InfluxSettings, hostname: str) -> None:
    with InfluxDBClient(url="", token=settings.token, org=settings.org) as client:
        write_api = client.write_api(write_options=SYNCHRONOUS)

        point = Point("climate") \
            .tag("host", hostname) \
            .field("temperature", climate_data.temperature) \
            .field("humidity", climate_data.humidity) \
            .time(datetime.utcnow(), WritePrecision.NS)

        write_api.write(settings.bucket, settings.org, point)


def get_temperature() -> float:
    try:
        temperature_sensor = W1ThermSensor()
    except NoSensorFoundError as e:
        logging.debug(e)
        temperature_sensor = None
    except SensorNotReadyError as e:
        logging.debug(e)
        time.sleep(1)
        temperature_sensor = W1ThermSensor()

    return temperature_sensor.get_temperature()


def get_humidity() -> float:
    """ Humidity sensor. Do not query faster than once per two seconds."""
    # initialize GPIO
    GPIO.setmode(GPIO.BCM)
    # read data using pin 17
    sensor = AOSONG.AM2320_1WIRE(pin=17)
    temperature_am2320 = None
    humidity = None
    try:
        temperature_am2320, humidity = sensor.readSensor()
    except AOSONG.DataError as e:
        logging.debug(f"AM2320 read error: {e}")
    return humidity


def main():
    filename = "settings.json"
    settings = read_settings(filename)
    print(settings)
    if settings is None:
        logging.debug("Error reading settings.json")

    logging.debug('InfluxDB server: ' + settings.url)
    climate = Climate()
    while True:
        climate.temperature = get_temperature()
        climate.humidity = get_humidity()
        hostname = socket.gethostname()
        write_climate_data(climate, settings, hostname)
        time.sleep(5)


if __name__ == '__main__':
    main()

GPIO.cleanup()
