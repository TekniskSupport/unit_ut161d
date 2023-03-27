include makefile.env

.PHONY: terminal-print
terminal-print:
		./terminal-print.py --interval=1
.PHONY: mqtt
mqtt:
		./mqtt-bridge.py --mqtt-host="$(MQTT_HOST)" --mqtt-topic="$(MQTT_TOPIC)" --interval=1
.PHONY: plotting-live-data
plotting-live-data:
		./plotting-live-data.py --interval=1
.PHONY: csv
csv:
		./reading-to-csv.py --interval=1
