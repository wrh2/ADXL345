"""

Python module for Analog Devices ADXL345 IMU

This module utilizes SPI on a Raspberry Pi3 to communicate with the IC

Programmed by William Harrington

wrh2.github.io

"""

import spidev
import RPi.GPIO as GPIO

SPI_BUS = 0
SPI_DEVICE = 0

CS_PIN = 18
CS_PIN_MODE = GPIO.OUT

READ = 1
WRITE = 0

RW_SHIFT = 7
MB_SHIFT = 6

WHO_AM_I = 0x0
POWER_CTL = 0x2D

DATAX0 = 0x32
DATAY0 = 0x34
DATAZ0 = 0x36

CPOL_HIGH = 1
CPOL_LOW = 0

CPHA_LEAD = 0
CPHA_TRAIL = 1

CPOL = CPOL_HIGH
CPHA = CPHA_TRAIL
CPOL_SHIFT = 1

MEASURE_MODE = 1
MEASURE_SHIFT = 3

class ADXL345:

    def __init__(self):
       self.__gpio_setup()
       self.__spi_setup()
       self.__write_data([(MEASURE_MODE << MEASURE_SHIFT)], POWER_CTL)

    def __exit__(self):
        GPIO.cleanup()

    def __gpio_setup(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(CS_PIN, CS_PIN_MODE)
        GPIO.output(CS_PIN, GPIO.HIGH)
       
    def __spi_setup(self):
        self.__spi = spidev.SpiDev()
        self.__spi.open(SPI_BUS, SPI_DEVICE)
        self.__spi.mode = (CPOL << CPOL_SHIFT) | CPHA

    def __read_data(self, L, addr):
        MB = int(L > 1)
        msg = (READ << RW_SHIFT) | (MB << MB_SHIFT) | addr
        GPIO.output(CS_PIN, GPIO.LOW)
        dummy_bytes = [0xFF for i in range(L)]
        to_send = [msg] + dummy_bytes
        result = self.__spi.xfer(to_send)
        GPIO.output(CS_PIN, GPIO.HIGH)
        return result[1:]

    def __write_data(self, d, addr):
        MB = int(len(d) > 1)
        msg = (WRITE << RW_SHIFT) | (MB << MB_SHIFT) | addr
        to_write = [msg] + d
        GPIO.output(CS_PIN, GPIO.LOW)
        self.__spi.xfer(to_write)
        GPIO.output(CS_PIN, GPIO.HIGH)

    def getX(self):
        data = self.__read_data(2, DATAX0)
        return ((data[0] << 8) | data[1])

    def getY(self):
        data = self.__read_data(2, DATAY0)
        return ((data[0] << 8) | data[1])

    def getZ(self):
        data = self.__read_data(2, DATAZ0)
        return ((data[0] << 8) | data[1])

    def getXYZ(self):
        data = self.__read_data(6, DATAX0)
        X = (data[0] << 8) | data[1]
        Y = (data[2] << 8) | data[3]
        Z = (data[4] << 8) | data[5]
        return X, Y, Z
