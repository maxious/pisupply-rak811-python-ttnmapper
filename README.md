# pisupply-rak811-python-ttnmapper
Python TTNMapper for RAK811 (AU915) in [IoT LoRa Node pHAT for Raspberry Pi](https://uk.pi-supply.com/products/iot-lora-node-phat-for-raspberry-pi)

Uses https://github.com/AmedeeBulle/pyrak811 and https://github.com/inmcm/micropyGPS

Set your keys in ttn_secrets.py

For AU915 on TTN (subband 2), config should look like:
```
$ rak811 get-config ch_list
0,off;1,off;2,off;3,off;4,off;5,off;6,off;7,off;
8,on,916800000,0,5;9,on,917000000,0,5;10,on,917200000,0,5;11,on,917400000,0,5;12,on,917600000,0,5;13,on,917800000,0,5;14,on,918000000,0,5;15,on,918200000,0,5;
16,off;17,off;18,off;19,off;20,off;21,off;22,off;23,off;24,off;25,off;26,off;27,off;28,off;29,off;30,off;31,off;
32,off;33,off;34,off;35,off;36,off;37,off;38,off;39,off;40,off;41,off;42,off;43,off;44,off;45,off;46,off;47,off;
48,off;49,off;50,off;51,off;52,off;53,off;54,off;55,off;56,off;57,off;58,off;59,off;60,off;61,off;62,off;63,off;
64,off;65,off;66,off;67,off;68,off;69,off;70,off;71,off

$ rak811 get-config ch_mask
0,ff00;1,0000;2,0000;3,0000;4,0000
```


GPS provided via I2C from [SparkFun GPS Breakout - Chip Antenna, SAM-M8Q (Qwiic)](https://www.sparkfun.com/products/15210)

Setting up I2C on the raspberry pi, you need to change the clock:
/etc/modprobe.d/i2c.conf

```
options i2c_bcm2708 baudrate=75000
```

/boot/config.txt:
```
dtparam=i2c_arm=on
# Clock stretching by slowing down to 7.5KHz
dtparam=i2c_arm_baudrate=75000
```
