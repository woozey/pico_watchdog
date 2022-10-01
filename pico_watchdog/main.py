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
from blinker import UPyBlinker

from connection_credentials import (SSID, WIFI_PASSWD, MQTT_PORT, MQTT_PASSWD,
                                    MQTT_SERVER, MQTT_USER)
from watch_targets import WATCH_TOPICS
from states import Context, DogState

WLAN_TIMEOUT = 5
BLINK_PERIOD = 1000  # ms
BLINK_DURATION = 200  # ms
BLINK_PIN = 'LED'
B_NUMBER_OK = 1
B_NUMBER_ALARM = 2
B_NUMBER_MQTT = 3
B_NUMBER_WIFI = 4
CHECK_INTERVAL = 6 * 60000  # ms

class DogCtx(Context):
    wifi = None
    mqtt = None
    target_data = dict(zip(WATCH_TOPICS, [None]*len(WATCH_TOPICS)))
    def __init__(self, state) -> None:
        super().__init__(state)
        self.last_check = time.ticks_add(time.ticks_ms(), -self.check_interval)
    
    def run(self):
        super().run()
        if time.ticks_diff(time.ticks_ms(), self.last_check) > self.check_interval:
            self.state.do_checks()
            self.last_check = time.time_ms()


class DDogState(DogState):
    blinker = UPyBlinker
    b_period = BLINK_PERIOD
    b_number = None
    b_duration = BLINK_DURATION
    b_pin = BLINK_PIN
    last_check = None
    check_interval = CHECK_INTERVAL
    
    def check_wifi(self):
        return self.context.wifi.status() == 3

    def check_mqtt(self):
        # dummy = self.context.mqtt
        return True

    def check_targets(self, targets_data):
        return True
    
    def mqtt_or_wifi_alarm(self):
        if not self.check_wifi():
            self.context.set_state(WiFiAlarm())
        else:
            self.context.set_state(MQTTAlarm())
    
    def ok_or_dog_alarm(self):
        if self.check_targets():
            self.context.set_state(OKState())
        else:
            self.context.set_state(DogAlarm())
    

class OKState(DDogState):
    b_number = B_NUMBER_OK
    
    def do_checks(self, *args):
        if not self.check_targets():
            if not self.check_mqtt():
                self.mqtt_or_wifi_alarm()
            else:
                self.context.set_state(DogAlarm())


class DogAlarm(DDogState):
    b_number = B_NUMBER_ALARM
      
    def do_checks(self, *args):
        if self.check_targets():
            self.context.set_state(OKState())
        else:
            if not self.check_mqtt():
                self.mqtt_or_wifi_alarm() 


class MQTTAlarm(DDogState):
    b_number = B_NUMBER_MQTT

    def do_checks(self):
        if self.check_mqtt():
            self.ok_or_dog_alarm()
        else:
            if not self.check_wifi():
                self.context.set_state(WiFiAlarm())


class WiFiAlarm(DDogState):
    b_number = B_NUMBER_WIFI

    def do_checks(self):
        if self.check_wifi():
            if self.check_mqtt():
                self.ok_or_dog_alarm()
            else:
                self.context.set_state(MQTTAlarm())


# Connect to WIFI
def run(ssid=None, wifi_passwd=None):
    ctx = DogCtx(DogAlarm())
    ctx.wifi = wifi_connect(ssid, wifi_passwd)
    ctx.mqtt = mqtt_connect()

    # Prepare  indicator LED
    # pin = Pin("LED", Pin.OUT)
    # start_time = time.ticks_ms()
    while True:
        for topic in WATCH_TOPICS:
            ctx.mqtt.subscribe(topic)
            ctx.run()
        # if time.ticks_diff(time.ticks_ms(), start_time) >= BLINK_INTERVAL:
        #     pin.toggle()
        #     start_time = time.ticks_ms()


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
