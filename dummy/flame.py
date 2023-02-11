import RPi.GPIO as GPIO
import time

# Set the GPIO mode
GPIO.setmode(GPIO.BCM)

# Set the GPIO pin for the flame sensor
FLAME_PIN = 18

# Set the pin as an input
GPIO.setup(FLAME_PIN, GPIO.IN)
BUZZ_PIN = 24

# Set the pin as an input
GPIO.setup(BUZZ_PIN, GPIO.OUT)
# Loop indefinitely
while True:
    # Read the value from the flame sensor
    flame_detected = GPIO.input(FLAME_PIN)

    # Check if the flame sensor has detected a flame
    if flame_detected:
        print("Flame detected!")
        GPIO.output(BUZZ_PIN,GPIO.HIGH)
    else:
        print("No flame detected.")
        GPIO.output(BUZZ_PIN,GPIO.LOW)

    # Wait for a short time before checking again
    time.sleep(0.5)
