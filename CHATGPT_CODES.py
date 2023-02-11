import smbus
import time

# Create an instance of the I2C bus
bus = smbus.SMBus(1)

# MAX30100 address
MAX30100_ADDRESS = 0x57

# Register addresses
REG_INT_STATUS = 0x00
REG_INT_ENABLE = 0x02
REG_FIFO_WRITE = 0x04
REG_FIFO_READ = 0x06
REG_FIFO_DATA = 0x07
REG_FIFO_CONFIG = 0x08
REG_MODE_CONFIG = 0x09
REG_SPO2_CONFIG = 0x0A
REG_LED_CONFIG = 0x0C

# Function to read data from a register
def read_register(address):
    return bus.read_byte_data(MAX30100_ADDRESS, address)

# Function to write data to a register
def write_register(address, data):
    bus.write_byte_data(MAX30100_ADDRESS, address, data)

# Configure the sensor
write_register(REG_INT_ENABLE, 0x00)
write_register(REG_FIFO_CONFIG, 0x0F)
write_register(REG_MODE_CONFIG, 0x03)
write_register(REG_SPO2_CONFIG, 0x27)
write_register(REG_LED_CONFIG, 0x24)

while True:
    # Read the data from the FIFO
    fifo_data = read_register(REG_FIFO_DATA)
    print("FIFO data: ", fifo_data)
    time.sleep(1)




import RPi.GPIO as GPIO
import time

# Set the GPIO pin numbers for the HX711 clock and data pins
CLK = 21
DAT = 20

# Set the reference unit for the HX711 sensor
referenceUnit = -1

def setupHX711():
    # Set the GPIO pin numbering mode
    GPIO.setmode(GPIO.BCM)
    # Set the clock and data pins as input
    GPIO.setup(CLK, GPIO.IN)
    GPIO.setup(DAT, GPIO.IN)
    # Wait for the HX711 to settle
    time.sleep(0.1)

def readHX711():
    # Pulse the clock pin 24 times to read the data
    data = 0
    for i in range(24):
        GPIO.output(CLK, True)
        data = data << 1
        GPIO.output(CLK, False)
        if(GPIO.input(DAT)):
            data += 1
    # Pulse the clock pin to read the parity bit
    GPIO.output(CLK, True)
    GPIO.output(CLK, False)
    # Check the parity bit and return the data
    if(GPIO.input(DAT)):
        data = data | 0x800000
    return data

def getWeight(referenceUnit):
    # Set the clock pin low
    GPIO.output(CLK, False)
    # Read the data from the HX711 and return the weight in grams
    data = readHX711()
    weight = (data - referenceUnit) / -1000.0
    return weight

# Set up the HX711 sensor
setupHX711()
# Set the reference unit for the sensor
referenceUnit = readHX711()
# Continuously read and print the weight in grams
while True:
    weight = getWeight(referenceUnit)
    print("Weight: {:.3f} g".format(weight))
    time.sleep(0.5)


import smbus
import time

# ADXL345 constants
EARTH_GRAVITY_MS2   = 9.80665
SCALE_MULTIPLIER    = 0.004

DATA_FORMAT         = 0x31
BW_RATE             = 0x2C
POWER_CTL           = 0x2D

BW_RATE_1600HZ      = 0x0F
BW_RATE_800HZ       = 0x0E
BW_RATE_400HZ       = 0x0D
BW_RATE_200HZ       = 0x0C
BW_RATE_100HZ       = 0x0B
BW_RATE_50HZ        = 0x0A
BW_RATE_25HZ        = 0x09

RANGE_2G            = 0x00
RANGE_4G            = 0x01
RANGE_8G            = 0x02
RANGE_16G           = 0x03

MEASURE             = 0x08
AXES_DATA           = 0x32

class ADXL345:

    address = None

    def __init__(self, address=0x53):
        self.address = address
        self.bus = smbus.SMBus(1)
        self.bus.write_byte_data(self.address, POWER_CTL, MEASURE)
        self.bus.write_byte_data(self.address, DATA_FORMAT, RANGE_2G)
        self.bus.write_byte_data(self.address, BW_RATE, BW_RATE_100HZ)

    def getAxes(self):
        bytes = self.bus.read_i2c_block_data(self.address, AXES_DATA, 6)

        x = bytes[0] | (bytes[1] << 8)
        if(x & (1 << 16 - 1)):
            x = x - (1<<16)

        y = bytes[2] | (bytes[3] << 8)
        if(y & (1 << 16 - 1)):
            y = y - (1<<16)

        z = bytes[4] | (bytes[5] << 8)
        if(z & (1 << 16 - 1)):
            z = z - (1<<16)

        x = x * SCALE_MULTIPLIER
        y = y * SCALE_MULTIPLIER
        z = z * SCALE_MULTIPLIER

        return {"x": x, "y": y, "z": z}

adxl345 = ADXL345()

while True:
    axes = adxl345.getAxes()
    print "ADXL345 on address 0x%x:" % (adxl345.address)
    print "   x = %.3fG" % ( axes['x'] )
    print "   y = %.3fG" % ( axes['y'] )
    print "   z = %.3fG" % ( axes['z'] )

