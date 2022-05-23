# ADXL345 Python Module

A simple python module for controlling an ADXL345 via SPI with a raspberry pi 3.

[Polling example](./examples/example_poll.py)

For help on how to use, check the [wiki](https://github.com/wrh2/ADXL345/wiki)

## Dependencies

[spidev](https://pypi.org/project/spidev/)

[RPi.GPIO](https://pypi.org/project/RPi.GPIO/)

## Features

* Configurable Chip Select
    * Can be controlled by the module via a GPIO or by the SPI peripheral
* Supports 2g, 4g, 8g, 16g scales
* Supports raw output or calculated output
* [Provides interface for directly reading/writing registers on the ADXL345](https://github.com/wrh2/ADXL345/wiki#going-beyond)

## About

Every example that I could find for the ADXL345 was written in either C or python, and, with the exception of a few C examples, they all used I2C.
I needed to use the ADXL345 via SPI to test some code I had written for another project so I created this module.
After talking with a colleague that had trouble using SPI with Python on a raspberry pi, I decided to share this here.

The code was written for and tested on a raspberry pi 3 with Python 2.7 and Python 3.4

## Tests

A unit test framework for the module using python's unittest module is [included](./tests/tests.py).

## TODO

* Configure interrupts for Activity/Inactivity, free-fall, tap detection
* Add more tests (e.g. test scaling factors when not in full-resolution mode)
* Incorporate FIFO use