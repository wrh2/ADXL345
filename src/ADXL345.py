"""

Python module for Analog Devices ADXL345 IMU

This module utilizes SPI on a Raspberry Pi3 to communicate with the IC

Programmed by William Harrington

wrh2.github.io

"""

from ctypes import c_int16
import spidev
import RPi.GPIO as GPIO

DEFAULT_SPI_BUS = 0
DEFAULT_SPI_DEVICE = 0

DEFAULT_CS_PIN = 18
DEFAULT_CS_PIN_MODE = GPIO.OUT

SPI_BUS = DEFAULT_SPI_BUS
SPI_DEVICE = DEFAULT_SPI_DEVICE

# Note: This is for software controlled chip select
#       Change according to the GPIO you would like to use
CS_PIN = DEFAULT_CS_PIN
CS_PIN_MODE = DEFAULT_CS_PIN_MODE

READ = 1
WRITE = 0

# RW bit position
RW_SHIFT = 7

# multibyte bit position
MB_SHIFT = 6

# register addresses
WHO_AM_I = 0x0
BW_RATE = 0x2C
POWER_CTL = 0x2D
DATA_FORMAT = 0x31
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

ADXL345_WHO_AM_I_VAL = 0xE5

MEASURE_MODE = 1
MEASURE_SHIFT = 3

FULL_RES = 1
FULL_RES_SHIFT = 3

SELF_TEST = 1
SELF_TEST_SHIFT = 7

G = 9.81

ACC_SCALE_2G = 0
ACC_SCALE_4G = 1
ACC_SCALE_8G = 2
ACC_SCALE_16G = 3

ACC_SENSITIVITY_2G = 3.9 * 1e-3 * G # mg/LSB
ACC_SENSITIVITY_4G = 7.8 * 1e-3 * G
ACC_SENSITIVITY_8G = 15.6 * 1e-3 * G
ACC_SENSITIVITY_16G = 31.2 * 1e-3 * G

OUTPUT_DATA_RATE_100HZ = 0xA
OUTPUT_DATA_RATE_200HZ = 0xB
OUTPUT_DATA_RATE_400HZ = 0xC
OUTPUT_DATA_RATE_800HZ = 0xD
OUTPUT_DATA_RATE_1600HZ = 0xE
OUTPUT_DATA_RATE_3200HZ = 0xF

DEFAULT_SENSITIVITY = ACC_SENSITIVITY_2G
DEFAULT_SCALE = ACC_SCALE_2G
DEFAULT_ODR = OUTPUT_DATA_RATE_100HZ

X_DATA_SIZE = 2    # bytes
Y_DATA_SIZE = 2
Z_DATA_SIZE = 2
XYZ_DATA_SIZE = 6
BW_RATE_DATA_SIZE = 1
WHO_AM_I_DATA_SIZE = 1
DATA_FORMAT_SIZE = 1

def MAKE_INT16(x,y):
    return ((x << 8) | y)

# def TWOS_COMPLEMENT(x, bits=16):
#     mask = 2**(bits-1)
#     return -(x & mask) + (x & ~mask)

class ADXL345:

    def __init__(self, sensitivity=DEFAULT_SENSITIVITY, scale=DEFAULT_SCALE, odr=DEFAULT_ODR, full_resolution=True, software_cs=False):
        
       # sets up private constants
       self.__constants(sensitivity, scale, full_resolution, software_cs)

       if self.__software_cs:

           # software is controlling chip select
           # set up gpio to do this
           self.__gpio_setup()
       
       self.__spi_setup()
       self.__getWhoAmI()
       self.__configure_accelerometer(odr, scale)

    def __exit__(self):
        
        if self.__software_cs:
            GPIO.cleanup()

    def __constants(self, sensitivity, scale, full_resolution, software_cs):

        self.__full_resolution = full_resolution

        if self.__full_resolution:

            # according to ADXL345 datasheet
            # in full resolution mode the sensitivity
            # is always 3.9mg/LSB
            self.__sensitivity = ACC_SENSITIVITY_2G

        else:

            self.__sensitivity = sensitivity
            
        self.__scale = (1 << scale)
        
        self.__software_cs = software_cs
        
    def __gpio_setup(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(CS_PIN, CS_PIN_MODE)
        GPIO.output(CS_PIN, GPIO.HIGH)
       
    def __spi_setup(self):
        self.__spi = spidev.SpiDev()
        self.__spi.open(SPI_BUS, SPI_DEVICE)
        self.__spi.mode = (CPOL << CPOL_SHIFT) | CPHA

    def __configure_accelerometer(self, odr, scale):

        # output data rate
        self.__odr_setup(odr)

        # sets full resolution mode and scale (2g/4g/8g/16g)
        self.__full_res(scale)

        # this actually turns the sensor on,
        # after this measurements become available
        # in the data registers
        self.__measurement_setup()

    def __odr_setup(self, odr):
        self.__write_data(BW_RATE, [odr])

    def __full_res(self, scale):
        self.__write_data(DATA_FORMAT, [(self.__full_resolution << FULL_RES_SHIFT) | scale])

    def __measurement_setup(self):
        self.__write_data(POWER_CTL, [(MEASURE_MODE << MEASURE_SHIFT)])

    def __multibyte(self, d):
        # determines if we are reading/writing multiple bytes
        return int(d > 1)
        
    def __read_data(self, addr, L):
        """
        This function is used for reading bytes from the ADXL345
        """

        MB = self.__multibyte(L)
        
        msg = (READ << RW_SHIFT) | (MB << MB_SHIFT) | addr

        dummy_bytes = [0xFF for i in range(L)]

        to_send = [msg] + dummy_bytes

        # for software controlled chip select
        if self.__software_cs:
            GPIO.output(CS_PIN, GPIO.LOW)

        result = self.__spi.xfer(to_send)

        # for software controlled chip select
        if self.__software_cs:
            GPIO.output(CS_PIN, GPIO.HIGH)
            
        return result[1:]

    def __write_data(self, addr, d):
        """
        This function is used for writing bytes from the ADXL345
        """

        MB = self.__multibyte(len(d))
        
        msg = (WRITE << RW_SHIFT) | (MB << MB_SHIFT) | addr

        to_write = [msg] + d

        # for software controlled chip select
        if self.__software_cs:
            GPIO.output(CS_PIN, GPIO.LOW)
            
        self.__spi.xfer(to_write)

        # for software controlled chip select
        if self.__software_cs:
            GPIO.output(CS_PIN, GPIO.HIGH)

    def __calculate_result(self, x):

        result = None

        if self.__full_resolution:

            result = self.__sensitivity * x

        else:

            result = self.__sensitivity * self.__scale * x

        return result

    def __getWhoAmI(self):
        """
        This function reads the WHO_AM_I register
        and returns the data to the user
        """
        data = self.__read_data(WHO_AM_I, WHO_AM_I_DATA_SIZE)

        self.__whoAmI = data[0]

    def readRegister(self, addr, L):
        """
        Public version of function for reading bytes from ADXL345
        """
        return self.__read_data(addr, L)

    def writeRegister(self, addr, d):
        """
        Public version of function for writing bytes from ADXL345

        d should be a list
        e.g. [byte0, byte1, byte2, ... , byte N]
        """
        self.__write_data(addr, d)
        
    def getX(self, raw=True):
        
        data = self.__read_data(DATAX0, X_DATA_SIZE)
        
        result = MAKE_INT16(data[1], data[0])

        if not raw:
            result = self.__calculate_result(c_int16(result).value)
            
        return result

    def getY(self, raw=True):
        
        data = self.__read_data(DATAY0, Y_DATA_SIZE)
        
        result = MAKE_INT16(data[1], data[0])

        if not raw:
            result = self.__calculate_result(c_int16(result).value)
            
        return result

    def getZ(self, raw=True):
        
        data = self.__read_data(DATAZ0, Z_DATA_SIZE)
        
        result = MAKE_INT16(data[1], data[0])

        if not raw:
            result = self.__calculate_result(c_int16(result).value)
            
        return result

    def getXYZ(self, raw=True):

        data = self.__read_data(DATAX0, XYZ_DATA_SIZE)

        X = MAKE_INT16(data[1], data[0])
        Y = MAKE_INT16(data[3], data[2])
        Z = MAKE_INT16(data[5], data[4])

        result = X, Y, Z

        if not raw:
            result = tuple([self.__calculate_result(c_int16(ele).value) for ele in result])

        return result

    @property
    def whoAmI(self):
        return self.__whoAmI
