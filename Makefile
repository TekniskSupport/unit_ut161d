.PHONY: terminal-print
terminal-print:
		./terminal-print.py --interval=1
.PHONY: mqtt
mqtt:
		./mqtt-bridge.py --mqtt-host="192.168.1.25" --mqtt-topic="dmm/temp" --interval=1
.PHONY: plotting-live-data
plotting-live-data:
		./plotting-live-data.py --interval=1
.PHONY: csv
csv:
		./reading-to-csv.py --interval=1
