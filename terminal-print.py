#!/usr/bin/env python3

import csv
import logging
import datetime
import argparse
import time

import decimal
from ut61eplus import UT61EPLUS

log = logging.getLogger(__name__)
cmdline : dict = None
dmm : UT61EPLUS = None

def read_data():
    log.debug('record data')
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
    log.debug('writing %s', data)

    return data

def write_data(data, count=0):
    if count==0:
        print(data.keys())
        print(data.values())
    else:
        print("%s %s" % (data['value'], data['unit']))
    count+=1
    return count

def main():
    global cmdline, dmm

    parser = argparse.ArgumentParser(description='csv')
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

    count = 0
    while True:
        try:
            count = write_data(read_data(), count)
            time.sleep(cmdline.interval)
        except Exception:
            log.exception('error in loop')
            time.sleep(10)

if __name__ == '__main__':
    main()
