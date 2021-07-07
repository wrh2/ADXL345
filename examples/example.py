"""

Example use of ADXL345 module

In this example the X,Y,Z values are polled on the ADXL345
Numpy is then used to convert them in to signed 16-bit integers
Samples are taken approximately every 300ms

Programmed by William Harrington

wrh2.github.io

"""

from ADXL345 import *
import numpy as np
import time
import sys

def main():

    # start the IC
    my_imu = ADXL345()

    while 1:
        
        #print('XYZ: %s' % np.int16(my_imu.getXYZ()))
        print('XYZ: %s' % list(my_imu.getXYZ(raw=False)))

        time.sleep(.3)

if __name__ == '__main__':
    
    try:
        
        main()
        
    except Exception as e:
        
        print('Caught Exception %s' % e)

        sys.exit(0)
