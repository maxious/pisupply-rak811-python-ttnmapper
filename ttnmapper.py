#!/usr/bin/python3
import sys
if sys.version_info < (3,0):
    print("We're not using the other versions anymore")
    sys.exit(0)

BLINKT = True
DISPLAYOTRON = False
GPSD_GPS = True
I2C_GPS = False

from gpspoller import I2CGpsPoller, my_gps, GpsdPoller
if BLINKT:
    from blinkt import set_pixel, set_all, show
if DISPLAYOTRON:
    import dothat.backlight as backlight
    import dothat.lcd as lcd

import csv
from random import randint
from sys import exit
from time import sleep, strftime
from datetime import datetime
from rak811 import Mode, Rak811
from ttn_secrets import APPS_KEY, DEV_ADDR, NWKS_KEY


import array
import traceback
NaN = float('nan')
def isnan(x): return str(x) == 'nan'

csvfile = open('gpslog-%s.csv'%strftime("%Y%m%d-%H%M%S"), 'w')
csvwriter = csv.writer(csvfile)
csvwriter.writerow(['timestamp','valid','lat','lon','altitude','hdop','sats'])

lora = Rak811()

# Most of the setup should happen only once...
if BLINKT:
    set_pixel(1,255,128,0,0.1)
    show()
if DISPLAYOTRON:
    lcd.clear()
    backlight.rgb(255,128,0)
    lcd.write("Starting up....")
print("Starting ttnmapper %s" % datetime.now().isoformat())
print("LoRa Hard Reset  %s" % datetime.now().isoformat())
lora.hard_reset()
print("LoRa Setup  %s" % datetime.now().isoformat())
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

print("Joining %s" % datetime.now().isoformat())
lora.join_abp()
lora.dr = 5
print("Joined %s" % datetime.now().isoformat())

print('Sending packets every 10 seconds - Interrupt to cancel loop')

print('You can send downlinks from the TTN console')
if I2C_GPS:
	gpsp = I2CGpsPoller() # create the thread
if GPSD_GPS:
	gpsp = GpsdPoller() # create the thread

try:
    gpsp.start() # start it up
    while True:
        valid = False
        print(gpsp.gpsd)
        if GPSD_GPS and  gpsp.gpsd:
            # https://gitlab.com/gpsd/gpsd/-/tree/master/gps
            #print( gpsp.gpsd.fix.latitude,', ', gpsp.gpsd.fix.longitude,'Accuracy: ', gpsp.gpsd.fix.epv,' Time: ', gpsp.gpsd.utc)
            latitude =  gpsp.gpsd.fix.latitude
            longitude =  gpsp.gpsd.fix.longitude
            altitude = gpsp.gpsd.fix.altitude if not isnan(gpsp.gpsd.fix.altitude) else 0
            hdop =  gpsp.gpsd.hdop
            valid =  gpsp.gpsd.fix.mode > 1
            sats =  gpsp.gpsd.satellites
            #print("Status: STATUS_%s" % ("NO_FIX", "FIX", "DGPS_FIX")[ gpsp.gpsd.fix.status])
            #print("Mode: MODE_%s" % ("ZERO", "NO_FIX", "2D", "3D")[ gpsp.gpsd.fix.mode])
            #print("Quality: %d p=%2.2f h=%2.2f v=%2.2f t=%2.2f g=%2.2f\n" %  (gpsd.satellites_used, gpsd.pdop, gpsd.hdop, gpsd.vdop, gpsd.tdop, gpsd.gdop))
        if I2C_GPS:
            latitude =  ( -1 if my_gps.latitude[2] == 'S' else 1) * (my_gps.latitude[0] + (my_gps.latitude[1] / 60))
            longitude = ( -1 if my_gps.longitude[2] == 'S' else 1) * (my_gps.longitude[0] + (my_gps.longitude[1] / 60))
            altitude =  my_gps.altitude
            hdop =  my_gps.hdop
            valid = my_gps.valid
            sats = my_gps.satellites_in_use
            print('Parsed Strings:', my_gps.gps_segments)
            print('Sentence CRC Value:', hex(my_gps.crc_xor))
            print('Longitude:', longitude )
            print('Latitude',  latitude)
            print('Altitude:', my_gps.altitude)
            print('UTC Timestamp:', my_gps.timestamp)
            print('Horizontal Dilution of Precision:', my_gps.hdop)
            print('Satellites in Use by Receiver:', my_gps.satellites_in_use)
            print('Data is Valid:', my_gps.valid)
        if valid:
            print("Valid GPS %s" % datetime.now().isoformat())
            #blue light
            if BLINKT:
                set_pixel(1,0,255,0,0.1)
                show()
            if DISPLAYOTRON:
                lcd.clear()
                backlight.rgb(0, 0, 255)
                lcd.write(valid,hdop, latitude, longitude, altitude)
            print("Build packet %s" % datetime.now().isoformat())
            #https://github.com/ttn-be/ttnmapper/blob/master/ttnmapper.py
            # https://github.com/ttn-be/gps-node-examples/blob/master/Sodaq/sodaq-one-ttnmapper/decoder.js
            data = array.array('B', [0, 0, 0, 0, 0, 0, 0, 0, 0])
            lat = int(((latitude + 90) / 180) * 16777215)
            data[0] = (lat >> 16) & 0xff
            data[1] = (lat >> 8) & 0xff
            data[2] = lat & 0xff

            lon = int(((longitude + 180) / 360) * 16777215)
            data[3] = (lon >> 16) & 0xff
            data[4] = (lon >> 8) & 0xff
            data[5] = lon & 0xff

            alt = int(altitude)
            data[6] = (alt >> 8) & 0xff
            data[7] = alt & 0xff

            dop = int(hdop * 10)
            data[8] = dop & 0xff

            message = bytes(data)
            print("Send packet %s" % datetime.now().isoformat())
            lora.send(data=message, confirm=False, port=1)
            #green light
            if BLINKT:
                set_pixel(1,0,0,255,0.1)
                show()
            if DISPLAYOTRON:
                lcd.clear()
                backlight.rgb(0, 255,0)
                lcd.write("SENT",hdop, latitude, longitude, altitude)
            #while lora.nb_downlinks:
            #    print('Received', lora.get_downlink()['data'])
            csvwriter.writerow([datetime.now().isoformat(),valid,latitude,longitude,altitude,hdop,sats])
        else:
            print("Invalid GPS %s" % datetime.now().isoformat())
            #red light
            if BLINKT:
                set_pixel(1,128,0,0,0.1)
                show()
            if DISPLAYOTRON:
                lcd.clear()
                backlight.rgb(255, 0, 0)
                lcd.write(valid,hdop, latitude, longitude, altitude)
            csvwriter.writerow([datetime.now().isoformat(),valid,None,None,None,None,sats if 'sats' in vars() else None])
        print("---")
        print()
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

