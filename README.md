# pisupply-rak811-python-ttnmapper
Python TTNMapper for RAK811 (AU915) in [IoT LoRa Node pHAT for Raspberry Pi](https://uk.pi-supply.com/products/iot-lora-node-phat-for-raspberry-pi)

Uses https://github.com/AmedeeBulle/pyrak811 so set your keys in ttn_secrets.py

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
