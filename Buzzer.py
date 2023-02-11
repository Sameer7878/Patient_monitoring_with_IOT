import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
BUZZ_PIN = 21

# Set the pin as an input
GPIO.setup(BUZZ_PIN, GPIO.OUT)
while True:
    time.sleep(1)
    GPIO.output(BUZZ_PIN,GPIO.HIGH)
    print('on')
    time.sleep(1)
    GPIO.output(BUZZ_PIN,GPIO.LOW)
    print('off')
    
