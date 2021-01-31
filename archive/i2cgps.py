#!/usr/bin/python
import time
import smbus
from micropyGPS import MicropyGPS
my_gps = MicropyGPS()
address = 0x42
gpsReadInterval = 0.3

BUS = smbus.SMBus(1)
while True:
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
    print('Parsed Strings:', my_gps.gps_segments)
    print('Sentence CRC Value:', hex(my_gps.crc_xor))
    print('Longitude:', ( -1 if my_gps.longitude[2] == 'S' else 1) * (my_gps.longitude[0] + (my_gps.longitude[1] / 60)))
    print('Latitude',  ( -1 if my_gps.latitude[2] == 'S' else 1) * (my_gps.latitude[0] + (my_gps.latitude[1] / 60)))
    print('UTC Timestamp:', my_gps.timestamp)
    print('Horizontal Dilution of Precision:', my_gps.hdop)
    print('Satellites in Use by Receiver:', my_gps.satellites_in_use)
    print('Data is Valid:', my_gps.valid)

    time.sleep(gpsReadInterval)
