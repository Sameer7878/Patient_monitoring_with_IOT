import Adafruit_ADS1x15
import time
adc = Adafruit_ADS1x15.ADS1115(address=0x48, busnum=1)

GAIN = 2/3

while 1:
    value = [0]
    value[0] = adc.read_adc(0, gain=GAIN)
    volts = value[0] / 32767.0 * 6.144
    psi = 50.0 * volts-25.0
    bar = psi * 0.0689475729
    print(bar)
    time.sleep(1)
