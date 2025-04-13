from machine import Pin, PWM
import dht
import time

# Color Constants for SHowing colors
COLOR_OFF = (0, 0, 0)
COLOR_WHITE = (1023, 1023, 1023)
COLOR_BLUE = (0, 0, 1023)
COLOR_GREEN = (0, 1023, 0)
COLOR_YELLOW = (1023, 1023, 0)
COLOR_ORANGE = (1023, 600, 0)
COLOR_RED = (1023, 0, 0)
COLOR_PURPLE = (600, 0, 600)
COLOR_CYAN = (0, 1023, 1023)
COLOR_PINK = (1023, 0, 1023)

pwm_freq = 1000

# Using PIN for rgb 25-27 pins are usually for general use
red_pwm = PWM(Pin(25), freq=pwm_freq)
green_pwm = PWM(Pin(26), freq=pwm_freq)
blue_pwm = PWM(Pin(27), freq=pwm_freq)

# For interrupt
DEBOUNCE_TIME = 200
INTERRUPT_DURATION = 2000 

# Setting r,g,b to 0 for no color
red_pwm.duty(0)
green_pwm.duty(0)
blue_pwm.duty(0)



class HumiditySensor:
    def __init__(self, dht_pin):
        self.interrupt_active = False
        self.interrupt_start_time = 0
        self.interrupt_color = 0
        self.last_left_interrupt = 0
        self.last_right_interrupt = 0
        
        self.dht_sensor = dht.DHT22(Pin(dht_pin))
        
        time.sleep(2)

        self.switch_left = Pin(14, Pin.IN, Pin.PULL_UP)
        self.switch_right = Pin(12, Pin.IN, Pin.PULL_UP)
        self.switch_left.irq(trigger=Pin.IRQ_FALLING, handler=self.left_switch_handler)
        self.switch_right.irq(trigger=Pin.IRQ_FALLING, handler=self.right_switch_handler)
        
    def set_color_to_rgb_led(self, r, g, b):
        red_pwm.duty(r)
        green_pwm.duty(g)
        blue_pwm.duty(b)
        time.sleep(0.5)

    def update_led_color_based_on_humidity(self, h):
        if h < 30:
            self.set_color_to_rgb_led(*COLOR_OFF)
        elif h < 40:
            self.set_color_to_rgb_led(*COLOR_WHITE)
        elif h < 50:
            self.set_color_to_rgb_led(*COLOR_BLUE)
        elif h < 60:
            self.set_color_to_rgb_led(*COLOR_GREEN)
        elif h < 70:
            self.set_color_to_rgb_led(*COLOR_YELLOW)
        elif h < 80:
            self.set_color_to_rgb_led(*COLOR_ORANGE)
        elif h < 90:
            self.set_color_to_rgb_led(*COLOR_RED)
        else:
            self.set_color_to_rgb_led(*COLOR_PURPLE)

    def read_humidity(self):
        try:
            self.dht_sensor.measure() 
            
            humidity = self.dht_sensor.humidity()
            temperature = self.dht_sensor.temperature()
            print(f"Humidity: {humidity:.1f}% | Temperature: {temperature:.1f}°C")
            
            return humidity, temperature
        except Exception as e:
            print(f"Error Reading Sensor: {e}")
            return None, None
        

    def left_switch_handler(self, pin):
        now = time.ticks_ms()
        
        if time.ticks_diff(now, self.last_left_interrupt) < DEBOUNCE_TIME:
            return
        
        self.last_left_interrupt = now
        
        if not self.interrupt_active:
            self.interrupt_active = True
            self.interrupt_start_time = now
            self.interrupt_color = 2  # Pink
            print("Left switch pressed (Pink)")

    def right_switch_handler(self, pin):
        now = time.ticks_ms()
        
        if time.ticks_diff(now, self.last_right_interrupt) < DEBOUNCE_TIME:
            return
        
        self.last_right_interrupt = now
        
        if not self.interrupt_active:
            self.interrupt_active = True
            self.interrupt_start_time = now
            self.interrupt_color = 1  # Cyan
            print("Right switch pressed (Cyan)")

    def check_and_handle_interrupt(self):
        # Checking if interrupt is active and change the color to either cyan or pink based on interrupt active or inactive 
        if self.interrupt_active:
            now = time.ticks_ms()
            
            if self.interrupt_color == 1:
                self.set_color_to_rgb_led(*COLOR_CYAN)
            
            elif self.interrupt_color == 2:
                self.set_color_to_rgb_led(*COLOR_PINK)
            
            if time.ticks_diff(now, self.interrupt_start_time) >= INTERRUPT_DURATION:
                self.interrupt_active = False
                self.interrupt_color = 0
                print("Interrupt ended")