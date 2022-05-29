"""
Example use of ADXL345 module with data ready interrupt

Programmed by William Harrington
wrh2.github.io
"""
from ADXL345 import *
import RPi.GPIO as GPIO
import time
import sys

global my_imu

def my_callback(channel):
    try:
        # logic is active high
        if GPIO.input(channel):
            print('Accelerometer data [X, Y, Z]: {0}'.format(my_imu.getXYZ())) # for raw data, imu.getAccData(raw=True)
    except Exception as e:
            print('Caught exception %s' % e)
            GPIO.cleanup()
            sys.exit(0)

def gpio_setup():
    # GPIO setup on raspberry pi for data ready interrupts
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.add_event_detect(17, GPIO.RISING, callback=my_callback)

def main():
    global my_imu

    # setup GPIO first otherwise it'll miss the first interrupt
    gpio_setup()

    my_imu = ADXL345(odr=ADXL345_OUTPUT_DATA_RATE_1_56HZ, interrupt_enable=True)

    while 1:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            GPIO.cleanup()
            del(my_imu)
            sys.exit(0)
        except Exception as e:
            print('Caught exception %s' % e)
            GPIO.cleanup()
            del(imu)
            sys.exit(0)

if __name__ == '__main__':
    main()
