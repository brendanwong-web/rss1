#!/usr/bin/env python3
import asyncio
from typing import Set

import csv
from typing import Optional
from fastapi import Request
from fastapi.responses import RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware
import paho.mqtt.client as mqtt

from nicegui import run, ui, app

MQTT_HOST = '192.168.1.250'
MQTT_PORT = 1883

with ui.row().classes('items-center'):
    connections_label = ui.label('0')
    ui.label('connections')
# open the file in the write mode

class Data:
    weight = 0
    
    def __init__(self):
        self.weight = 12123
    def update_weight(self, w):
        self.weight = w
        print('written weight from class', self.weight)
        
passwords = {'user1': 'pass1', 'user2': 'pass2'}

unrestricted_page_routes = {'/login'}
        
local_data = {'weight': 1212,}
data = Data()


def update_data(x):
    global local_data
    local_data['weight'] = x
    connections_label.text = x
    print("weight in local_data: ", local_data.get('weight', 0))
    data.update_weight(x)
    print("weight in data: ", data.weight)
    
    
def on_connect(client, userdata, flags, reason_code, properties):
    print(f"Connected with result code {reason_code}")
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("weight")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    update_data(str(msg.payload.decode()))
    print(msg.topic+" "+str(msg.payload.decode()))
    
def on_subscribe(client, obj, mid, reason_code_list):
    print("Subscribed: " + str(mid) + " " + str(reason_code_list))
    ui.notify('arssgarsg')
    
mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
mqttc.on_connect = on_connect
mqttc.on_message = on_message

mqttc.connect("192.168.1.250", 1883, 60)
    
with ui.column().classes('ml-4'):
    ui.label().bind_text_from(data, 'weight')
    ui.label().bind_text_from(local_data, 'weight')


mqttc.loop_start() 

ui.run()


