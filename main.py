#!/usr/bin/env python3
"""This is just a simple authentication example.

Please see the `OAuth2 example at FastAPI <https://fastapi.tiangolo.com/tutorial/security/simple-oauth2/>`_  or
use the great `Authlib package <https://docs.authlib.org/en/v0.13/client/starlette.html#using-fastapi>`_ to implement a classing real authentication system.
Here we just demonstrate the NiceGUI integration.
"""
from typing import Optional, List
from models import SignUpSchema, LoginSchema
from fastapi import Request
from fastapi.responses import RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware
import paho.mqtt.client as mqtt
import requests
import json
from datetime import datetime

from nicegui import app, ui
from pocketbase import PocketBase  # Client also works the same
from pocketbase.client import FileUpload

client = PocketBase('http://127.0.0.1:8090')


#DB

# in reality users passwords would obviously need to be hashed
unrestricted_page_routes = {'/login', '/register', '/test'}

#MQTT
MQTT_HOST = '192.168.1.250'
MQTT_PORT = 1883
mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

class Data:
    weight = 0
    material = ''
    points = ''
    user_id = ''
    
    def __init__(self):
        self.weight = 12123
    def update_weight(self, w, m):
        self.weight = w
        self.material = m
        print('written weight from class', self.weight)
    def update_points(self, uid, points):
        self.user_id = uid
        self.points = self.weight * 1.5
        print('written data from class')
        
local_data = {'weight': 1212,}

data = Data()

class AuthMiddleware(BaseHTTPMiddleware):
    """This middleware restricts access to all NiceGUI pages.

    It redirects the user to the login page if they are not authenticated.
    """

    async def dispatch(self, request: Request, call_next):
        if not app.storage.user.get('authenticated', False):
            if not request.url.path.startswith('/_nicegui') and request.url.path not in unrestricted_page_routes:
                app.storage.user['referrer_path'] = request.url.path  # remember where the user wanted to go
                return RedirectResponse('/login')
        return await call_next(request)

app.add_middleware(AuthMiddleware)

mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

def update_data(x, t):
    global local_data
    local_data['weight'] = x
    print("weight in local_data: ", local_data.get('weight', 0))
    data.update_weight(x, t)
    print("weight in data: ", data.weight)
    
def on_connect(client, userdata, flags, reason_code, properties):
    print(f"Connected with result code {reason_code}")
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("weight")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    update_data(str(msg.payload.decode()), msg.topic)
    print(msg.topic+" "+str(msg.payload.decode()))
    
def on_subscribe(client, obj, mid, reason_code_list):
    print("Subscribed: " + str(mid) + " " + str(reason_code_list))
    ui.notify('arssgarsg')

mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
mqttc.connect(MQTT_HOST, MQTT_PORT, 60)
mqttc.on_connect = on_connect
mqttc.on_message = on_message

@ui.page('/')
def main_page() -> None:
    def logout() -> None:
        app.storage.user.clear()
        ui.navigate.to('/login')

    with ui.column().classes('absolute-center items-center mb-8'):
        ui.label(f'Hello {app.storage.user["username"]}!').classes('text-5xl mb-8')      
        ui.label("Welcome to recycling sorting center")
        ui.link('Start recycling', "/test")
        ui.button(on_click=logout, icon='logout').props('outline round').classes('mt-8')

def update_db():
    print('update db')

@ui.page('/submit/{username}')
def submit_data(username: str) -> None:
    global data
    with ui.column().classes('absolute-center items-center mb-8'):
        with ui.row():
            ui.label(f'Submitted data for {username}')
        with ui.row():
            ui.label(f"Weight: {local_data.get('weight')}")
            # ui.label("Weight: " + str(data.weight))
        
    
    # TODO write to db


@ui.page('/login')
def login() -> Optional[RedirectResponse]:
    '''def try_login() -> None:  # local function to avoid passing username and password as arguments
        if passwords.get(username.value) == password.value:
            app.storage.user.update({'username': username.value, 'authenticated': True})
            ui.navigate.to(app.storage.user.get('referrer_path', '/'))  # go back to where the user wanted to go
        else:
            ui.notify('Wrong username or password', color='negative')'''
    async def try_login() -> None:
        authData = client.collection('users').auth_with_password(username.value, password.value)
        app.storage.user.update(
            {
                'username': authData.record.username,
                'email': authData.record.email,
                'authenticated': True,
                'user_id': authData.record.id,
                'created': authData.record.created,
            }
        )
        #print(type(authData.record.id))
        data.update_points(authData.record.id, 0)
        if not authData.is_valid:
            ui.notify("invalid login details")
        ui.navigate.to(app.storage.user.get('referrer_path', '/'))
        
        
    with ui.card().classes('absolute-center'):
        username = ui.input('Username').on('keydown.enter', try_login)
        password = ui.input('Password', password=True, password_toggle_button=True).on('keydown.enter', try_login)
        ui.button('Log in', on_click=try_login)
        with ui.row():
            ui.label("Don\'t have an account yet?")
            ui.link('Register', "/register")

@ui.page('/register')
def register() -> None:
    def try_register() -> None:  # local function to avoid passing username and password as arguments
        data = {
            "username": username.value,
            "email": email.value,
            "emailVisibility": True,
            "password": password.value,
            "passwordConfirm": password2.value,
            "name": username.value
            }
        print(data)
        try:
            result = client.collection("users").create(data)
            # print(result)
            ui.notify("Account succesfully created!")
            ui.navigate.to("/")
        except Exception as error:
            ui.notify(error.data['data']['password']['message'])
            #ui.notify(error.data['message'])
            
    if app.storage.user.get('authenticated', False):
        return RedirectResponse('/')
    with ui.card().classes('absolute-center'):
        username = ui.input('Username').on('keydown.enter', try_register)
        email = ui.input('Email').on('keydown.enter', try_register)
        password = ui.input('Password', password=True, password_toggle_button=True).on('keydown.enter', try_register)
        password2 = ui.input('Password', password=True, password_toggle_button=True).on('keydown.enter', try_register)
        ui.button('Register', on_click=try_register)
    
@ui.page('/test')
def test():
    def set_transaction():
        if (data.material == ''):
            data.material = 'paper'
        transaction = {
                "material": data.material,
                "weight": data.weight,
                "points": data.points,
                "time": str(datetime.now()),
                "user_id": app.storage.user.get('user_id')
        };
        try:
            record = client.collection('transactions').create(transaction);
        except Exception as error:
            print(error.data['data'])
        ui.notify("data sent")
    with ui.column().classes('absolute-center items-center mb-8'):
        with ui.row():  
                ui.label("Weight of Plastic recycled: ").classes('text-2xl')
                ui.label().bind_text_from(data, 'weight').classes('text-2xl font-bold')
        with ui.row():
            ui.label("Weight of paper recycled: ").classes('text-2xl')
            ui.label().bind_text_from(local_data, 'weight').classes('text-2xl font-bold')
        with ui.row():
            ui.button('Confirm data', on_click=set_transaction)
        with ui.row():
            urlstring = '/submit/' + app.storage.user["username"]
            ui.link('Submit data', urlstring)
    
if __name__ in {'__main__', '__mp_main__'}:
    mqttc.loop_start() 
    ui.run(storage_secret='stasrtrt')
    