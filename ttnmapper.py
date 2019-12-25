#!/usr/bin/python3
from random import randint
from sys import exit
from time import sleep

from rak811 import Mode, Rak811
from ttn_secrets import APPS_KEY, DEV_ADDR, NWKS_KEY

from blinkt import set_pixel, set_all, show

import array
import traceback
import time
import smbus
from micropyGPS import MicropyGPS
my_gps = MicropyGPS()
address = 0x42
gpsReadInterval = 0.3

BUS = smbus.SMBus(1)

import threading


class GpsPoller(threading.Thread):
  def __init__(self):
    threading.Thread.__init__(self)
    self.current_value = None
    self.running = True #setting the thread running to true

  def run(self):
    global my_gps
    while gpsp.running:
        try:
            while True: # Newline, or bad char.
                c = BUS.read_byte(address)
                if c == 255:
                    break
                elif c == 10:
                    break
                else:
                    if c > 90:
                        c = ord(",")
                    my_gps.update(chr(c))
            sleep(gpsReadInterval)
        except IOError:
            print("Reconnecting i2c bus...")
            sleep(0.5)
            connectBus()


lora = Rak811()

# Most of the setup should happen only once...
set_pixel(1,255,128,0,0.1)
show()
print('LoRa Hard Reset')
lora.hard_reset()
print('LoRa Setup')
lora.mode = Mode.LoRaWan
lora.band = 'AU915'
# ttn subband 2 setup
# https://github.com/PiSupply/IoTLoRaRange/blame/master/IoT%20LoRa%20Raspberry%20Pi%20Node%20pHAT/README.md#L98
lora.set_config(ch_mask = '0,FF00')
lora.set_config(ch_mask = '1,0000')
lora.set_config(ch_mask = '2,0000')
lora.set_config(ch_mask = '3,0000')
lora.set_config(ch_mask = '4,0000')
lora.set_config(dev_addr=DEV_ADDR,
                apps_key=APPS_KEY,
                nwks_key=NWKS_KEY)

print('Joining')
lora.join_abp()
lora.dr = 5
print('Joined')

print('Sending packets every 10 seconds - Interrupt to cancel loop')
print('You can send downlinks from the TTN console')
gpsp = GpsPoller() # create the thread

try:
    gpsp.start() # start it up
    while True:
        print('Parsed Strings:', my_gps.gps_segments)
        print('Sentence CRC Value:', hex(my_gps.crc_xor))
        print('Longitude:', ( -1 if my_gps.longitude[2] == 'S' else 1) * (my_gps.longitude[0] + (my_gps.longitude[1] / 60)))
        print('Latitude',  ( -1 if my_gps.latitude[2] == 'S' else 1) * (my_gps.latitude[0] + (my_gps.latitude[1] / 60)))
        print('Altitude:', my_gps.altitude)
        print('UTC Timestamp:', my_gps.timestamp)
        print('Horizontal Dilution of Precision:', my_gps.hdop)
        print('Satellites in Use by Receiver:', my_gps.satellites_in_use)
        print('Data is Valid:', my_gps.valid)

        if my_gps.valid:
            #blue light
            set_pixel(1,0,255,0,0.1)
            show()
            print('Build packet')
            #https://github.com/ttn-be/ttnmapper/blob/master/ttnmapper.py
            # https://github.com/ttn-be/gps-node-examples/blob/master/Sodaq/sodaq-one-ttnmapper/decoder.js
            data = array.array('B', [0, 0, 0, 0, 0, 0, 0, 0, 0])
            latitude =  ( -1 if my_gps.latitude[2] == 'S' else 1) * (my_gps.latitude[0] + (my_gps.latitude[1] / 60))
            lat = int(((latitude + 90) / 180) * 16777215)
            data[0] = (lat >> 16) & 0xff
            data[1] = (lat >> 8) & 0xff
            data[2] = lat & 0xff

            longitude = ( -1 if my_gps.longitude[2] == 'S' else 1) * (my_gps.longitude[0] + (my_gps.longitude[1] / 60))
            lon = int(((longitude + 180) / 360) * 16777215)
            data[3] = (lon >> 16) & 0xff
            data[4] = (lon >> 8) & 0xff
            data[5] = lon & 0xff

            alt = int(my_gps.altitude)
            data[6] = (alt >> 8) & 0xff
            data[7] = alt & 0xff

            hdop = int(my_gps.hdop * 10)
            data[8] = hdop & 0xff

            message = bytes(data)
            print('Send packet')
            lora.send(data=message, confirm=False, port=1)
            #green light
            set_pixel(1,0,0,255,0.1)
            show()
            #while lora.nb_downlinks:
            #    print('Received', lora.get_downlink()['data'])
        else:
            #red light
            set_pixel(1,128,0,0,0.1)
            show()
        sleep(10)
except (KeyboardInterrupt, SystemExit): #when you press ctrl+c
    print("\nKilling Thread...")
    gpsp.running = False
    gpsp.join() # wait for the thread to finish what it's doing
    print("Done.\nExiting.")
except Exception as e:  # noqa
    print(e)
    traceback.print_exc()
    pass

print('Cleaning up')
lora.close()
exit(0)
