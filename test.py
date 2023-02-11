import time
import Rasp_Sensor_Codes as rc
from multiprocessing import Process ,Queue

def runInParallel(*fns):
  proc = []
  for fn in fns:
    p = Process(target=fn)
    p.start()
    proc.append(p)
  for p in proc:
    p.join()

mx30 = rc.MAX30100()
mx30.enable_spo2()
#mx30.get_values()
flame=rc.Fire_detect(18,24)
acc=rc.Accelerometer()
#acc.detect()
oxy_pres=rc.Oxygen_Pressure(0x48)
#spo2.get_values()
#process_spo2=Process(target=mx30.get_values)
#process_flame=Process(target=flame.detect)
#process_acc=Process(target=acc.detect)
#process_oxy_pres=Process(target=oxy_pres)
while True:
    output_que=Queue()
    runInParallel(mx30.get_values(output_que),flame.detect(output_que),acc.detect(output_que),oxy_pres.get_values(output_que))

#i2c=busio.I2C(board.SCL,board.SDA)
#accelerometer = adafruit_adxl34x.ADXL345(i2c,address=0x57)
'''while True:
    #print("%f %f %f"%accelerometer.acceleration)
    time.sleep(0.5)
    mx30.read_sensor()

    mx30.ir, mx30.red

    hb = int(mx30.ir / 100)
    spo2 = int(mx30.red / 100)
    
    if mx30.ir != mx30.buffer_ir :
        print("Pulse:",hb);
    if mx30.red != mx30.buffer_red:
        print("SPO2:",spo2);
    
    else:
        print('Reading')
    time.sleep(2)'''