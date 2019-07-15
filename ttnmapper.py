from random import randint
from sys import exit
from time import sleep

from rak811 import Mode, Rak811
from ttn_secrets import APPS_KEY, DEV_ADDR, NWKS_KEY

lora = Rak811()

# Most of the setup should happen only once...
print('Setup')
lora.hard_reset()
lora.mode = Mode.LoRaWan
lora.band = 'AU915'
lora.set_config(dev_addr=DEV_ADDR,
                apps_key=APPS_KEY,
                nwks_key=NWKS_KEY)

print('Joining')
lora.join_abp()
lora.dr = 5

print('Sending packets every 10 seconds - Interrupt to cancel loop')
print('You can send downlinks from the TTN console')
try:
    while True:
        print('Send packet')
        #https://github.com/ttn-be/ttnmapper/blob/master/ttnmapper.py
        # https://github.com/ttn-be/gps-node-examples/blob/master/Sodaq/sodaq-one-ttnmapper/decoder.js
        data = array.array('B', [0, 0, 0, 0, 0, 0, 0, 0, 0])

        lat = int(((nmea.latitude + 90) / 180) * 16777215)
        data[0] = (lat >> 16) & 0xff
        data[1] = (lat >> 8) & 0xff
        data[2] = lat & 0xff

        lon = int(((nmea.longitude + 180) / 360) * 16777215)
        data[3] = (lon >> 16) & 0xff
        data[4] = (lon >> 8) & 0xff
        data[5] = lon & 0xff

        alt = int(nmea.altitude)
        data[6] = (alt >> 8) & 0xff
        data[7] = alt & 0xff

        hdop = int(nmea.hdop * 10)
        data[8] = hdop & 0xff

        message = bytes(data)
        # Cayenne lpp random value as analog
        lora.send(data=bytes.fromhex('0102{:04x}'.format(randint(0, 0x7FFF))), confirm=False, port=1)

        while lora.nb_downlinks:
            print('Received', lora.get_downlink()['data'])

        sleep(10)
except:  # noqa
    pass

print('Cleaning up')
lora.close()
exit(0)
