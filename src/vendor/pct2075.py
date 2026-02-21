# PCT2075 class
from machine import I2C


DEFAULT_ADDRESS = 0x37

class PCT2075:
    def __init__(self, i2c_bus: I2C, address=DEFAULT_ADDRESS):
        self.i2c = i2c_bus
        self.address = address

        # cached readings
        self._temperature = None

    @property
    def temperature(self):
        data = self.i2c.readfrom_mem(self.address, 0x00, 2)
        temp = (data[0] << 3) | (data[1] >> 5)
        if temp & 0x400:
            temp -= 1 << 11
        return temp * 0.125