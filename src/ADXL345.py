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

"""
Note from datasheet

Use of the 3200 Hz and 1600 Hz output data rates is only recommended with SPI communication
rates greater than or equal to 2 MHz.

The 800 Hz output data rate is recommended only for communication speeds greater than or equal to 400 kHz,
and the remaining data rates scale proportionally.

For example, the minimum recommended communication speed for a 200 Hz output data rate is 100 kHz.
"""
ADXL345_DEFAULT_SPI_BITRATE = int(2e6) # 2MHz

ADXL345_WHO_AM_I_VAL = 0xE5

ADXL345_ACC_SCALE_2G = 0
ADXL345_ACC_SCALE_4G = 1
ADXL345_ACC_SCALE_8G = 2
ADXL345_ACC_SCALE_16G = 3

ADXL345_ACC_SENSITIVITY_2G_MIN = 3.5 * 1e-3 * 9.81 # mg/LSB
ADXL345_ACC_SENSITIVITY_2G_TYP = 3.9 * 1e-3 * 9.81
ADXL345_ACC_SENSITIVITY_2G_MAX = 4.3 * 1e-3 * 9.81

ADXL345_ACC_SENSITIVITY_4G_MIN = 7.1 * 1e-3 * 9.81 # mg/LSB
ADXL345_ACC_SENSITIVITY_4G_TYP = 7.8 * 1e-3 * 9.81
ADXL345_ACC_SENSITIVITY_4G_MAX = 8.7 * 1e-3 * 9.81

ADXL345_ACC_SENSITIVITY_8G_MIN = 14.1 * 1e-3 * 9.81 # mg/LSB
ADXL345_ACC_SENSITIVITY_8G_TYP = 15.6 * 1e-3 * 9.81
ADXL345_ACC_SENSITIVITY_8G_MAX = 17.5 * 1e-3 * 9.81

ADXL345_ACC_SENSITIVITY_16G_MIN = 28.6 * 1e-3 * 9.81 # mg/LSB
ADXL345_ACC_SENSITIVITY_16G_TYP = 31.2 * 1e-3 * 9.81
ADXL345_ACC_SENSITIVITY_16G_MAX = 34.5 * 1e-3 * 9.81

ADXL345_OUTPUT_DATA_RATE_0_10HZ = 0x0
ADXL345_OUTPUT_DATA_RATE_0_20HZ = 0x1
ADXL345_OUTPUT_DATA_RATE_0_39HZ = 0x2
ADXL345_OUTPUT_DATA_RATE_0_78HZ = 0x3
ADXL345_OUTPUT_DATA_RATE_1_56HZ = 0x4
ADXL345_OUTPUT_DATA_RATE_3_13HZ = 0x5
ADXL345_OUTPUT_DATA_RATE_6_25HZ = 0x6
ADXL345_OUTPUT_DATA_RATE_12_5HZ = 0x7
ADXL345_OUTPUT_DATA_RATE_25HZ = 0x8
ADXL345_OUTPUT_DATA_RATE_50HZ = 0x9
ADXL345_OUTPUT_DATA_RATE_100HZ = 0xA
ADXL345_OUTPUT_DATA_RATE_200HZ = 0xB
ADXL345_OUTPUT_DATA_RATE_400HZ = 0xC
ADXL345_OUTPUT_DATA_RATE_800HZ = 0xD
ADXL345_OUTPUT_DATA_RATE_1600HZ = 0xE
ADXL345_OUTPUT_DATA_RATE_3200HZ = 0xF

ADXL345_DEFAULT_SENSITIVITY = ADXL345_ACC_SENSITIVITY_2G_TYP
ADXL345_DEFAULT_SCALE = ADXL345_ACC_SCALE_2G
ADXL345_DEFAULT_ODR = ADXL345_OUTPUT_DATA_RATE_100HZ

def MAKE_INT16(x,y):
    return ((x << 8) | y)

class ADXL345:

    def __init__(self, sensitivity=ADXL345_DEFAULT_SENSITIVITY, scale=ADXL345_DEFAULT_SCALE, odr=ADXL345_DEFAULT_ODR, full_resolution=True, software_cs=False, bitrate=ADXL345_DEFAULT_SPI_BITRATE):
        
       # sets up private constants
       self.__constants(sensitivity, scale, full_resolution, software_cs)

       if self.__software_cs:

           # software is controlling chip select
           # set up gpio to do this
           self.__gpio_setup()
       
       self.__bitrate = bitrate
       self.__spi_setup()

       self.__setupRegisterMap()

       self.__whoAmI = None
       self.__getWhoAmI()

       self.__configure_accelerometer(odr, scale)

    def __setupRegisterMap(self):

        # register map for ADXL345
        self.regs = {
            'DEVID': 0x0,
            'THRESH_TAP': 0x1D,
            'OFSX': 0x1E,
            'OFSY': 0x1F,
            'OFSZ': 0x20,
            'DUR': 0x21,
            'Latent': 0x22,
            'Window': 0x23,
            'THRESH_ACT': 0x24,
            'THRESH_INACT': 0x25,
            'TIME_INACT': 0x26,
            'ACT_INACT_CTL': 0x27,
            'THRESH_FF': 0x28,
            'TIME_FF': 0x29,
            'TAP_AXES': 0x2A,
            'ACT_TAP_STATUS': 0x2B,
            'BW_RATE': 0x2C,
            'POWER_CTL': 0x2D,
            'INT_ENABLE': 0x2E,
            'INT_MAP': 0x2F,
            'INT_SOURCE': 0x30,
            'DATA_FORMAT': 0x31,
            'DATAX0': 0x32,
            'DATAX1': 0x33,
            'DATAY0': 0x34,
            'DATAY1': 0x35,
            'DATAZ0': 0x36,
            'DATAZ1': 0x37,
            'FIFO_CTL': 0x38,
            'FIFO_STATUS': 0x39,
        }

    def __power_down(self):
        if self.__spi:
            self.__measurement_off()
            self.__spi.close()

    def __exit__(self):
        self.__power_down()
        if self.__software_cs:
            GPIO.cleanup()

    def __constants(self, sensitivity, scale, full_resolution, software_cs):

        self.__full_resolution = full_resolution

        if self.__full_resolution:

            # according to ADXL345 datasheet
            # in full resolution mode the sensitivity
            # is always 3.9mg/LSB
            self.__sensitivity = ADXL345_ACC_SENSITIVITY_2G_TYP

        else:

            self.__sensitivity = sensitivity
            
        self.__scale = (1 << scale)
        
        self.__software_cs = software_cs
        
    def __gpio_setup(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(CS_PIN, CS_PIN_MODE)
        GPIO.output(CS_PIN, GPIO.HIGH)
       
    def __spi_setup(self):

        # clock polarity
        CPOL_LOW = 0
        CPOL_HIGH = 1

        # clock phase
        CPHA_LEAD = 0
        CPHA_TRAIL = 1

        # CPHA = 1, CPOL =1
        CPOL = CPOL_HIGH
        CPHA = CPHA_TRAIL

        CPOL_SHIFT = 1

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
        self.__measurement_on()

    def __odr_setup(self, odr):
        BW_RATE = self.regs['BW_RATE']
        self.__write_data(BW_RATE, [odr])

    def __full_res(self, scale):
        FULL_RES_SHIFT = 3
        DATA_FORMAT = self.regs['DATA_FORMAT']
        self.__write_data(DATA_FORMAT, [(self.__full_resolution << FULL_RES_SHIFT) | scale])

    def __measurement_on(self):

        POWER_CTL = self.regs['POWER_CTL']
        POWER_CTL_DATA_SIZE = 1

        reg_data = self.__read_data(POWER_CTL, POWER_CTL_DATA_SIZE)[0]

        MEASURE_MODE = 1
        MEASURE_SHIFT = 3

        reg_data |= (MEASURE_MODE << MEASURE_SHIFT)

        self.__write_data(POWER_CTL, [reg_data])

    def __measurement_off(self):

        POWER_CTL = self.regs['POWER_CTL']
        # POWER_CTL_DATA_SIZE = 1

        # reg_data = self.__read_data(POWER_CTL, POWER_CTL_DATA_SIZE)[0]

        # MEASURE_MODE = 1
        # MEASURE_SHIFT = 3
        
        # reg_data &= ~(MEASURE_MODE << MEASURE_SHIFT)

        self.__write_data(POWER_CTL, [0])

    def __multibyte(self, d):
        # determines if we are reading/writing multiple bytes
        return int(d > 1)
        
    def __read_data(self, addr, L):
        """
        This function is used for reading bytes from the ADXL345
        """
        ADXL345_READ_BIT = 1
        ADXL345_RW_SHIFT = 7 # RW bit position
        ADXL345_MB_SHIFT = 6 # multibyte bit position

        MB = self.__multibyte(L)
        
        msg = (ADXL345_READ_BIT << ADXL345_RW_SHIFT) | (MB << ADXL345_MB_SHIFT) | addr

        dummy_bytes = [0xFF for i in range(L)]

        to_send = [msg] + dummy_bytes

        # for software controlled chip select
        if self.__software_cs:
            GPIO.output(CS_PIN, GPIO.LOW)

        result = self.__spi.xfer(to_send, self.__bitrate)

        # for software controlled chip select
        if self.__software_cs:
            GPIO.output(CS_PIN, GPIO.HIGH)
            
        return result[1:]

    def __write_data(self, addr, d):
        """
        This function is used for writing bytes from the ADXL345
        """
        ADXL345_WRITE_BIT = 0
        ADXL345_RW_SHIFT = 7 # RW bit position
        ADXL345_MB_SHIFT = 6 # multibyte bit position


        MB = self.__multibyte(len(d))
        
        msg = (ADXL345_WRITE_BIT << ADXL345_RW_SHIFT) | (MB << ADXL345_MB_SHIFT) | addr

        to_write = [msg] + d

        # for software controlled chip select
        if self.__software_cs:
            GPIO.output(CS_PIN, GPIO.LOW)
            
        self.__spi.xfer(to_write, self.__bitrate)

        # for software controlled chip select
        if self.__software_cs:
            GPIO.output(CS_PIN, GPIO.HIGH)

    def __calculate_result(self, x):

        result = self.__sensitivity * x

        return result

    def __getWhoAmI(self):
        """
        This function reads the WHO_AM_I register
        and returns the data to the user
        """
        WHO_AM_I = self.regs['DEVID']
        WHO_AM_I_DATA_SIZE = 1
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
        
        X_DATA_SIZE = 2
        DATAX0 = self.regs['DATAX0']

        data = self.__read_data(DATAX0, X_DATA_SIZE)
        
        result = MAKE_INT16(data[1], data[0])

        if not raw:
            result = self.__calculate_result(c_int16(result).value)
            
        return result

    def getY(self, raw=True):

        Y_DATA_SIZE = 2
        DATAY0 = self.regs['DATAY0']
        
        data = self.__read_data(DATAY0, Y_DATA_SIZE)
        
        result = MAKE_INT16(data[1], data[0])

        if not raw:
            result = self.__calculate_result(c_int16(result).value)
            
        return result

    def getZ(self, raw=True):

        Z_DATA_SIZE = 2
        DATAZ0 = self.regs['DATAZ0']
        
        data = self.__read_data(DATAZ0, Z_DATA_SIZE)
        
        result = MAKE_INT16(data[1], data[0])

        if not raw:
            result = self.__calculate_result(c_int16(result).value)
            
        return result

    def getXYZ(self, raw=True):

        XYZ_DATA_SIZE = 6
        DATAX0 = self.regs['DATAX0']

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
