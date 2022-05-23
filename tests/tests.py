from ADXL345 import *
import unittest

class TestADXL345(unittest.TestCase):

    def test_who_am_i(self):
        acc = ADXL345()
        self.assertEqual(acc.whoAmI, ADXL345_WHO_AM_I_VAL)

    def test_scale_2g(self):
        acc = ADXL345(full_resolution=False) # full resolution is default so explicitly turn off
        data = acc.getXYZ()
        c = [(d/ADXL345_ACC_SENSITIVITY_2G_TYP) for d in data]
        for (a,b) in zip(c, data):
            self.assertEqual((a*ADXL345_ACC_SENSITIVITY_2G_TYP), b)

    def test_scale_4g(self):
        acc = ADXL345(sensitivity=ADXL345_ACC_SENSITIVITY_4G_TYP, scale=ADXL345_ACC_SCALE_4G, full_resolution=False) # full resolution is default so explicitly turn off
        data = acc.getXYZ()
        c = [(d/ADXL345_ACC_SENSITIVITY_4G_TYP) for d in data]
        for (a,b) in zip(c, data):
            self.assertEqual((a*ADXL345_ACC_SENSITIVITY_4G_TYP), b)

    def test_scale_8g(self):
        acc = ADXL345(sensitivity=ADXL345_ACC_SENSITIVITY_8G_TYP, scale=ADXL345_ACC_SCALE_8G, full_resolution=False) # full resolution is default so explicitly turn off
        data = acc.getXYZ()
        c = [(d/ADXL345_ACC_SENSITIVITY_8G_TYP) for d in data]
        for (a,b) in zip(c, data):
            self.assertEqual((a*ADXL345_ACC_SENSITIVITY_8G_TYP), b)

    def test_scale_16g(self):
        acc = ADXL345(sensitivity=ADXL345_ACC_SENSITIVITY_16G_TYP, scale=ADXL345_ACC_SCALE_16G, full_resolution=False) # full resolution is default so explicitly turn off
        data = acc.getXYZ()
        c = [(d/ADXL345_ACC_SENSITIVITY_16G_TYP) for d in data]
        for (a,b) in zip(c, data):
            self.assertEqual((a*ADXL345_ACC_SENSITIVITY_16G_TYP), b)

    def test_full_res_2g(self):
        acc = ADXL345() # full resolution is default
        data = acc.getXYZ()
        c = [(d/ADXL345_ACC_SENSITIVITY_2G_TYP) for d in data]
        for (a,b) in zip(c, data):
            self.assertEqual((a*ADXL345_ACC_SENSITIVITY_2G_TYP), b)

    def test_full_res_4g(self):
        acc = ADXL345(scale=ADXL345_ACC_SCALE_4G) # full resolution is default
        data = acc.getXYZ()
        c = [(d/ADXL345_ACC_SENSITIVITY_2G_TYP) for d in data]
        for (a,b) in zip(c, data):
            self.assertEqual((a*ADXL345_ACC_SENSITIVITY_2G_TYP), b)

    def test_full_res_8g(self):
        acc = ADXL345(scale=ADXL345_ACC_SCALE_8G) # full resolution is default
        data = acc.getXYZ()
        c = [(d/ADXL345_ACC_SENSITIVITY_2G_TYP) for d in data]
        for (a,b) in zip(c, data):
            self.assertEqual((a*ADXL345_ACC_SENSITIVITY_2G_TYP), b)

    def test_full_res_16g(self):
        acc = ADXL345(scale=ADXL345_ACC_SCALE_16G) # full resolution is default
        data = acc.getXYZ()
        c = [(d/ADXL345_ACC_SENSITIVITY_2G_TYP) for d in data]
        for (a,b) in zip(c, data):
            self.assertEqual((a*ADXL345_ACC_SENSITIVITY_2G_TYP), b)

if __name__ == '__main__':
    unittest.main()
