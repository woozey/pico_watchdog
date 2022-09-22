# MIT License

# Copyright (c) 2022 Pico Watchdog developers

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
import time

import network
from machine import Pin
from umqtt.simple import MQTTClient

from connection_credentials import (SSID, WIFI_PASSWD, MQTT_PORT, MQTT_PASSWD,
                                    MQTT_SERVER, MQTT_USER)
from watch_targets import WATCH_TOPICS

WLAN_TIMEOUT = 5
BLINK_INTERVAL = 500  # ms

# Connect to WIFI
def run(ssid=None, wifi_passwd=None):
    wlan = wifi_connect(ssid, wifi_passwd)
    mqtt = mqtt_connect()

    # Prepare  indicator LED
    pin = Pin("LED", Pin.OUT)
    start_time = time.ticks_ms()
    while True:
        for topic in WATCH_TOPICS:
            mqtt.subscribe(topic)
        if time.ticks_diff(time.ticks_ms(), start_time) >= BLINK_INTERVAL:
            pin.toggle()
            start_time = time.ticks_ms()


def mqtt_connect(mqtt_server=None,
                 mqtt_port=None,
                 mqtt_user=None,
                 mqtt_passwd=None,
                 client_id='pico_watchdog'):
    if mqtt_server is None:
        mqtt_server = MQTT_SERVER
    if mqtt_port is None:
        mqtt_port = MQTT_PORT
    if mqtt_user is None:
        mqtt_user = MQTT_USER
    if mqtt_passwd is None:
        mqtt_passwd = MQTT_PASSWD
    
    client = MQTTClient(client_id,
                        mqtt_server,
                        port=mqtt_port,
                        user=mqtt_user,
                        password=mqtt_passwd)
    client.set_callback(mqtt_callback)
    client.connect()
    print(f'MQTT: connected to {mqtt_server}.')
    return client


def mqtt_callback(topic, msg):
    msg_time  = time.ticks_ms()
    print(f'Time: {msg_time}')
    print(f'Message in topic: {topic}')


def wifi_connect(ssid, wifi_passwd):
    if ssid is None:
        ssid = SSID
    if wifi_passwd is None:
        wifi_passwd = WIFI_PASSWD
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, wifi_passwd)

    time_elapsed = 0

    while time_elapsed < WLAN_TIMEOUT:
        if wlan.status() < 0 or wlan.status() >= 3:
            break
        time_elapsed += 1
        print('WLAN: waiting for connection...')
        time.sleep(1)

    if wlan.status() != 3:
        print(f'WLAN: cannot connect to {SSID} with status {wlan.status()}')
    else:
        print('connected')
        status = wlan.ifconfig()
        print( 'ip = ' + status[0] )
    return wlan
        
if __name__ == '__main__':
    run()
