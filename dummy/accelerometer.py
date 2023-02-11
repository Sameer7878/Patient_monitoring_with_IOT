import time
import board
import adafruit_adxl34x
import busio
i2c=busio.I2C(board.SCL,board.SDA)
print(i2c)
accelerometer = adafruit_adxl34x.ADXL345(i2c)

while True:
    x, y, z = accelerometer.acceleration
    print("X: {:.2f}  Y: {:.2f}  Z: {:.2f}".format(x, y, z))
    time.sleep(1)
