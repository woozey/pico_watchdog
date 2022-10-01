# pico_watchdog
Watchdog for HomeAssistant and MQTT connected devices to run or Raspberry Pi Pico W.

## Installation
Before to start download or use upip to install requierd libraries.

### Requirements
1. MQTT: `upip.install('umqtt')`
2. itertools: `upip.install('itertools')`
3. UPyBlinker, download from [github/woozey/blinker](https://github.com/woozey/blinker)

### Install blinker
Using rshell: 
```
mkdir /pyboard/lib/blinker
cp path_to_blinker/blinker/blinker.py /pyboard/lib/blinker
cp path_to_blinker/blinker/ublinker.py /pyboard/lib/blinker
```
