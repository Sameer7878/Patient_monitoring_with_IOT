import RPi.GPIO as gpio
import time

RS =18
EN =23
D4 =24
D5 =25
D6 =8
D7 =7

DT =27
SCK=17

m1=12
m2=1


LOW=0

gpio.setmode(gpio.BCM)
sample=0

val=0
gpio.setup(SCK, gpio.OUT)

gpio.setwarnings(False)

def readCount():
  i=0
  Count=0
  gpio.setup(DT, gpio.OUT)
  gpio.output(DT,0)
  gpio.output(SCK,0)
  print(gpio.input(DT))  
  #gpio.setup(DT, gpio.IN)
  print(gpio.input(DT))
  while gpio.input(DT) == 1:
      print('1') 
      i=0
  for i in range(24):
      gpio.output(SCK,1)
      Count=Count<<1
      gpio.output(SCK,0)
    #time.sleep(0.001)
      if gpio.input(DT) == 0:
          Count=Count+1
  print(Count)
  gpio.output(SCK,1)
  Count=Count^0x800000
  gpio.output(SCK,0)
  print(Count)
  return Count 

while 1:
    count= readCount()
    time.sleep(2)
    print (count)