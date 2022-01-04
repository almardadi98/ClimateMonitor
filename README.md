# ClimateMonitor

Þetta forrit dælir gögnum frá hita- og rakaskynjara í InfluxDB gagnagrunn. Grafana les svo gögnin og gerir falleg gröf úr þeim og birtir á "real time" dashboard. Grafana sendir alerts ef gildin fara yfir eða undir ákveðinn þröskuld. Skynjararnir eru tengdir í Raspberry Pi tölvu.

## voktun.service
Þetta er skrá sem skilgreinir systemd þjónustuna fyrir þetta forrit.


Environment variable "location" er hægt að nota til að aðskilja gögnin