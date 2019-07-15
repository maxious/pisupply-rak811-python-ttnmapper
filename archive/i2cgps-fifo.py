#!/usr/bin/python
import time
import json
import smbus
import logging 
import os, sys
# Path to be created
path = "/tmp/gps"
try:
    os.mkfifo(path)
except OSError, e:
    print "Failed to create FIFO: %s" % e
fifo = open(path, 'w')

BUS = None
address = 0x42
gpsReadInterval = 0.3

def connectBus():
    global BUS
    BUS = smbus.SMBus(1)

def parseResponse(gpsLine):
    gpsChars = ''.join(chr(c) for c in gpsLine)
    if "*" not in gpsChars:
        return False
#    print gpsChars
    gpsStr, chkSum = gpsChars.split('*')    
    gpsFixedStr = ""
    for ch in gpsStr:
        if ord(ch) > 90:
            gpsFixedStr += ","
        else:
            gpsFixedStr += ch

    chkVal = 0
    for ch in gpsFixedStr[1:]: # Remove the $
        chkVal ^= ord(ch)
    if (chkVal == int(chkSum, 16)):
#       print "yes"
       fifo.write(gpsFixedStr+"*"+chkSum+"\n")
       fifo.flush()
#    else:
#        for ch in gpsStr:
#            if ord(ch) > 90:
#                print ch, ord(ch)


def readGPS():
    c = None
    response = []
    try:
        while True: # Newline, or bad char.
            c = BUS.read_byte(address)
            if c == 255:
                return False
            elif c == 10:
                break
            else:
                response.append(c)
        parseResponse(response)
    except IOError:
        time.sleep(0.5)
        connectBus()
    except Exception, e:
        print e

connectBus()
while True:
    readGPS()
    time.sleep(gpsReadInterval)
