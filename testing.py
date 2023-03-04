import Rasp_Sensor_Codes as rc

motion=rc.Accelerometer()

while True:
    print(motion.detect())