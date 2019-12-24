#!/usr/bin/env python
# coding: utf-8

import paho.mqtt.client as mqtt
import time
import requests
import json
import os
import sys
import config
import api_lb
import random
import setenv

broker_address = os.environ.get('broker_address')
Topic = os.environ.get('Topic')
col_name = os.environ.get('col_name')

def on_message(client, userdata, message):
    m = str(message.payload.decode("utf-8")).split(',')
    print("message received: {}".format(m))

    uri = '{}?vals={}'.format(config.uri, json.dumps([col_name,m[1],m[3]]))
    url_list = api_lb.make_url_list(config.api_hosts, config.port, uri)

    err_msg = 'store API is not running'
    ret_vals = api_lb.connect_lb(url_list, err_msg, 'store')

print("creating new instance")
client = mqtt.Client() #create new instance
client.on_message=on_message #attach function to callback
print("connecting to broker")
client.connect(broker_address) #connect to broker

client.loop_start() #start the loop

while True:
    client.subscribe(Topic)
    time.sleep(2) # wait

client.loop_stop() #stop the loop



