#!/usr/bin/python
#Based on veproza proyect: https://gist.github.com/veproza/55ec6eaa612781ac29e7
import requests

#Edit me!!

print "Connecting to u-blox"
# alm is optional
r = requests.get("http://online-live1.services.u-blox.com/GetOnlineData.ashx?token=" + token + 
                 ";gnss=gps,glo,gal;datatype=eph,alm,aux,pos;filteronpos;format=mga" +
                 ";lat=-33;lon=151;alt=21;pacc=100"
                 , stream=True)
print "Downloading A-GPS data"

print "Writing AGPS data"
ser.write(r.content)
print "Done"

