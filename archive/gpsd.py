#! /usr/bin/python
# Written by Dan Mandle http://dan.mandle.me September 2012
# http://www.danmandle.com/blog/getting-gpsd-to-work-with-python/
# License: GPL 2.0
 
import os
from gps import *
from time import *
import time
import threading
 
gpsd = None #seting the global variable
gps_sky = None 
os.system('clear') #clear the terminal (optional)
 
class GpsPoller(threading.Thread):
  def __init__(self):
    threading.Thread.__init__(self)
    global gpsd #bring it in scope
    gpsd = gps(mode=WATCH_NEWSTYLE) #starting the stream of info
    self.current_value = None
    self.running = True #setting the thread running to true
 
  def run(self):
    global gpsd,gps_sky
    while gpsp.running:
      gpsd.next() #this will continue to loop and grab EACH set of gpsd info to clear the buffer
      print gpsd.data.get("class")
#      if gpsd['class'] == 'SKY':
#          gps_sky = gpsd
 
if __name__ == '__main__':
  gpsp = GpsPoller() # create the thread
  try:
    gpsp.start() # start it up
    while True:
      #It may take a second or two to get good data
#      os.system('clear')
      print gpsd.fix.latitude,', ',gpsd.fix.longitude,'Accuracy: ',gpsd.fix.epv,' Time: ',gpsd.utc
  
      print "Status: STATUS_%s\n" % ("NO_FIX", "FIX", "DGPS_FIX")[gpsd.fix.status]
      print "Mode: MODE_%s\n" % ("ZERO", "NO_FIX", "2D", "3D")[gpsd.fix.mode]
      print "Quality: %d p=%2.2f h=%2.2f v=%2.2f t=%2.2f g=%2.2f\n" % \
              (gpsd.satellites_used, gpsd.pdop, gpsd.hdop, gpsd.vdop, gpsd.tdop, gpsd.gdop)
      if gps_sky:
          print "Quality: %d p=%2.2f h=%2.2f v=%2.2f t=%2.2f g=%2.2f\n" % \
                  (gps_sky.satellites_used, gps_sky.pdop, gps_sky.hdop, gpsd.vdop, gpsd.tdop, gpsd.gdop)
      
      time.sleep(1) #set to whatever
 
  except (KeyboardInterrupt, SystemExit): #when you press ctrl+c
    print "\nKilling Thread..."
    gpsp.running = False
    gpsp.join() # wait for the thread to finish what it's doing
  print "Done.\nExiting."
