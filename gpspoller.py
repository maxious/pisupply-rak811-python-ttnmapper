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

def timeout(func, args=(), kwargs={}, timeout_duration=1, default=None):
    import signal

    class TimeoutError(Exception):
        pass

    def handler(signum, frame):
        print("timedout")
        raise TimeoutError()

    # set the timeout handler
    signal.signal(signal.SIGALRM, handler) 
    signal.alarm(timeout_duration)
    try:
        result = func(*args, **kwargs)
    except TimeoutError as exc:
        result = default
    finally:
        signal.alarm(0)

    return result

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

gpsd = None #seting the global variable
gps_sky = None
gps_tpv = None
#os.system('clear') #clear the terminal (optional)

class GpsdPoller(threading.Thread):
  def __init__(self):
    threading.Thread.__init__(self)
    global gpsd #bring it in scope
    gpsd = gps(mode=WATCH_NEWSTYLE) #starting the stream of info
    self.current_value = None
    self.running = True #setting the thread running to true

  def run(self):
    global gpsd,gps_sky,gps_tpv
    while self.running:
      print("gpsd polled", gpsd.data,  datetime.now().isoformat())
#      with Timeout(5.0) as timeout_ctx:
      gpsd.next()
      print("gpsd next'd", gpsd.data,  datetime.now().isoformat())
      print(gpsd.fix.latitude,gpsd.fix.longitude,'Accuracy: ',gpsd.fix.epv,' Time: ',gpsd.utc)
      print("Status: STATUS_%s\n" % ("NO_FIX", "FIX", "DGPS_FIX")[gpsd.fix.status])
      print("Mode: MODE_%s\n" % ("ZERO", "NO_FIX", "2D", "3D")[gpsd.fix.mode])
      print("Quality: %d p=%2.2f h=%2.2f v=%2.2f t=%2.2f g=%2.2f\n" %  (gpsd.satellites_used, gpsd.pdop, gpsd.hdop, gpsd.vdop, gpsd.tdop, gpsd.gdop))
      if gpsd.data.get("class") == 'SKY':
          gps_sky = gpsd
      if gpsd.data.get("class") == 'TPV':
          gps_tpv = gpsd

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
