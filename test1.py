'''from dummy.hx711 import HX711
print(1)
try:
    hx711 = HX711(dout_pin=27,pd_sck_pin=17,channel='A',gain=64)
    hx711.reset()   # Before we start, reset the HX711 (not obligate)
    measures = hx711.get_raw_data(num_measures=3)
finally:
    GPIO.cleanup()  # always do a GPIO cleanup in your scripts!

print("\n".join(measures))'''
