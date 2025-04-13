from machine import Pin, PWM
import time
from HumiditySensor import HumiditySensor

HUMIDITY_THRESHOLD = 80

sensor = HumiditySensor(dht_pin=4)


buzzer = PWM(Pin(13), freq=2000, duty=0)

while True:
    humidity, temperature = sensor.read_humidity()

    if humidity is not None:
        sensor.update_led_color_based_on_humidity(humidity)
        sensor.check_and_handle_interrupt()

        if humidity >= HUMIDITY_THRESHOLD:
            print("Humidity threshold exceeded!")    
            buzzer.duty(512)
        else:
            print(f"Humidity value is under threshold {humidity}%")
            buzzer.duty(0)      
    time.sleep(2)