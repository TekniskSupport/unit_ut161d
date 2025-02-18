#!/usr/bin/env python3

# pip3 install --user paho-mqtt

import paho.mqtt.client as mqtt
import json
import logging
import datetime
import argparse
import time

import decimal
from ut61eplus import UT61EPLUS

log = logging.getLogger(__name__)
cmdline : dict = None
dmm : UT61EPLUS = None

class MyClient(mqtt.Client):
    def __init__(self, mid):
        self._last_data : datetime = None
        super().__init__(mid)

    def loop(self, timeout=1.0, max_packets=1):
        log.debug('loop timeout=%f', timeout)
        if cmdline.interval < 5:
            timeout = 0.3
        res = super().loop(timeout, max_packets)

        now = datetime.datetime.now()
        if self._last_data is None:
            self._last_data = now
        elif (now - self._last_data).total_seconds() >= cmdline.interval:
            self._last_data = now
            send_data(self)

        return res

def send_data(client : mqtt.Client):
    log.debug('send data')
    m = dmm.takeMeasurement()
    log.debug('measurement=%s', m)
    v : str = None
    if m.value.is_infinite():
        v = 'overflow'
    else:
        v = '{0:f}'.format(m.value)

    data = {
        'mode': m.mode,
        'dc': m.isDC,
        'unit': m.unit,
        'value': v,
        'battery_warning': m.hasBatteryWarning,
    }
    log.debug('sending %s', data)
    client.publish(cmdline.mqtt_topic, json.dumps(data))

def on_connect(client, userdata, flags, rc):
    log.info('connected to mqtt')

def on_message(client, userdata, msg):
    print(msg.topic + ' ' + str(msg.payload))

def main():
    global cmdline, dmm

    parser = argparse.ArgumentParser(description='mqtt bridge')

    parser.add_argument('--mqtt-client-id', type=str, required=False, help='client id connecting to mqtt server')
    parser.add_argument('--mqtt-host', type=str, required=True, help='mqtt server')
    parser.add_argument('--mqtt-port', type=int, required=False, default=1883, help='mqtt server')
    parser.add_argument('--mqtt-user', type=str, required=False, help='mqtt username')
    parser.add_argument('--mqtt-password', type=str, required=False, help='mqtt password')

    parser.add_argument('--mqtt-topic', type=str, required=True, help='measurement topic')
    parser.add_argument('--interval', type=float, required=True, help='interval for measurement in seconds')

    parser.add_argument('--debug', required=False, action='store_true', help='enable debug logging')

    cmdline = parser.parse_args()
    log.debug('cmdline=%s', cmdline)

    if cmdline.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    log.info('opening DMM')
    dmm = UT61EPLUS()
    dmm_name = dmm.getName()
    log.info('DMM:%s', dmm_name)
    mqtt_name = cmdline.mqtt_client_id
    if mqtt_name is None:
        mqtt_name = dmm_name

    mqtt_client = MyClient(mqtt_name)
    mqtt_client.username_pw_set(cmdline.mqtt_user, cmdline.mqtt_password)
    mqtt_client.on_connect = on_connect
    mqtt_client.connect(cmdline.mqtt_host, cmdline.mqtt_port)

    while True:
        try:
            mqtt_client.loop(cmdline.interval)
        except Exception:
            log.exception('error in mqtt loop')
            time.sleep(10)

if __name__ == '__main__':
    main()
