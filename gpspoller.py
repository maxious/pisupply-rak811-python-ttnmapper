#!/usr/bin/python3
from time import sleep
from datetime import datetime

import smbus
from micropyGPS import MicropyGPS
#from stopit import Timeout
my_gps = MicropyGPS()
address = 0x42
gpsReadInterval = 0.3

BUS = smbus.SMBus(1)

import threading

class I2CGpsPoller(threading.Thread):
  def __init__(self):
    threading.Thread.__init__(self)
    self.current_value = None
    self.running = True #setting the thread running to true

  def run(self):
    global my_gps
    while self.running:
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

from gps import *
from time import *
import time
import threading


class GpsdPoller(threading.Thread):
  def __init__(self):
    threading.Thread.__init__(self)
    self.gpsd = gps(mode=WATCH_NEWSTYLE) #starting the stream of info
    self.current_value = None
    self.running = True #setting the thread running to true

  def run(self):
    while self.running:
      try:
          self.gpsd.next()
      except StopIteration:
          print("gpsd crashed, reconnecting")
          sleep(30)
          self.gpsd = gps(mode=WATCH_NEWSTYLE)
      if self.gpsd.data.get("class") == 'SKY':
          self.gps_sky = self.gpsd.data
      if self.gpsd.data.get("class") == 'TPV':
          self.gps_tpv = self.gpsd.data

if __name__ == "__main__":
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

            sleep(1)
    except (KeyboardInterrupt, SystemExit): #when you press ctrl+c
        print("\nKilling Thread...")
        gpsp.running = False
        gpsp.join() # wait for the thread to finish what it's doing
        print("Done.\nExiting.")
    except Exception as e:  # noqa
        print(e)
        traceback.print_exc()
        pass
