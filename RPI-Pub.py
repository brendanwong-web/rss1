#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Copyright (c) 2010-2013 Roger Light <roger@atchoo.org>
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Distribution License v1.0
# which accompanies this distribution.
#
# The Eclipse Distribution License is available at
#   http://www.eclipse.org/org/documents/edl-v10.php.
#
# Contributors:
#    Roger Light - initial implementation
# Copyright (c) 2010,2011 Roger Light <roger@atchoo.org>
# All rights reserved.

# This shows a simple example of an MQTT subscriber.


import paho.mqtt.client as mqtt
import csv
import time
import datetime
from paho.mqtt.properties import Properties
from paho.mqtt.packettypes import PacketTypes 

def on_connect(mqttc, obj, flags, reason_code):
    print("reason_code: " + str(reason_code))


def on_message(mqttc, obj, msg):
    print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))


def on_subscribe(mqttc, obj, mid, reason_code_list):
    print("Subscribed: " + str(mid) + " " + str(reason_code_list))



# If you want to use a specific client id, use
# mqttc = mqtt.Client("client-id")
# but note that the client id must be unique on the broker. Leaving the client
# id parameter empty will generate a random id for you.
mqttc = mqtt.Client()
mqttc.on_message = on_message
mqttc.on_connect = on_connect
mqttc.on_subscribe = on_subscribe
# Uncomment to enable debug messages
# mqttc.on_log = on_log
mqttc.connect("192.168.1.250", 1883, 60)


properties=Properties(PacketTypes.PUBLISH)
properties.MessageExpiryInterval=30 # in seconds
    
mqttc.loop_start()

for i in range(0, 50):
    b = i%3
    c = (i*5)%7
    d = i +2
    res = str(i) + str(b) + str(c) + str(d) + str(i) + str(i)
    mqttc.publish('weight',res,2,properties=properties);
    time.sleep(1)
    
mqttc.stop()    
