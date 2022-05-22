from ADXL345 import *
import unittest

class TestADXL345(unittest.TestCase):

    def test_who_am_i(self):
        acc = ADXL345()
        data = acc.whoAmI()
        self.assertEqual(data, ADXL345_WHO_AM_I_VAL)

if __name__ == '__main__':
    unittest.main()
