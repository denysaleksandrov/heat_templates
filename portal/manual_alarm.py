#!/usr/bin/env python
# encoding: utf-8

import os
import sys
import json
import random
import requests
from subprocess import Popen, PIPE
from pprint import pprint as pp

_, MODE = sys.argv

CONTROLLER = os.environ[u'CONTROLLER']
URL = u'http://{}:8197/alarms/api'.format(CONTROLLER)

def get_ids():
    pipe = Popen([u'ceilometer', u'alarm-list'], stdout=PIPE)
    alarms = pipe.stdout.readlines()[3:-1]
    if not alarms:
        print u'No Alarms found, please check "ceilometer alarm-list"'
    alarm_ids = []
    for i in alarms:
        alarm_ids.append(i.split('|')[1].lstrip().rstrip())
    return alarm_ids
    

def create():
    alarm_ids = get_ids()
    data = {}
    data[u'current'] = u'alarm'
    data[u'previous'] = u'ok'
    data[u'alarm_id'] = random.choice(alarm_ids)
    data[u'reason'] = u'Transition to alarm due to 1 samples outside threshold, most recent: 25'
    reason_data = {}
    reason_data[u'count'] = 1
    reason_data[u'most_recent'] = 24
    reason_data[u'type'] = u'threshold'
    reason_data[u'disposition'] = u'outside'
    data[u'reason_data'] = reason_data
    headers = {'Content-Type': 'application/json'}
    r = requests.post(URL, headers=headers, data=json.dumps(data))

def delete():
    alarm_ids = get_ids()
    data = {}
    data[u'current'] = u'ok'
    data[u'previous'] = u'alarm'
    data[u'alarm_id'] = random.choice(alarm_ids)
    data[u'reason'] = u'Transition to alarm due to 1 samples outside threshold, most recent: 5'
    reason_data = {}
    reason_data[u'count'] = 1
    reason_data[u'most_recent'] = 4
    reason_data[u'type'] = u'threshold'
    reason_data[u'disposition'] = u'inside'
    data[u'reason_data'] = reason_data
    headers = {u'Content-Type': u'application/json'}
    r = requests.post(URL, headers=headers, data=json.dumps(data))

if __name__ == '__main__':
    try:
        eval(MODE+ u'()')
    except:
        print u'Please check argumner you passed, it should be either "delete" or "create"'
