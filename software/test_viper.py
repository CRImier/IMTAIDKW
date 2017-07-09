from machine import Pin
from time import sleep
import network

wlan = network.WLAN(network.AP_IF)
wlan.active(True)
wlan.config(essid="\U0001F4A9", password="atpisies1337")

columns = [Pin(16, Pin.OUT), Pin(14, Pin.OUT), Pin(12, Pin.OUT), Pin(13, Pin.OUT)]

clock = Pin(5, Pin.OUT)
latch = Pin(4, Pin.OUT)
data = Pin(15, Pin.OUT)

@micropython.viper 
def shiftOut(data: int):
    GPIO_OUT = ptr32(0x60000300) # GPIO base register
    GPIO_OUT[2] = 0x10 # set latch pin to low
    for i in range(8):
        value = (data & 1<<i)>>i #1 if i'th bit is set, 0 if not set
        reg = 2-(value) #Selecting set or unset register - unset reg is 2, set reg is 1
        GPIO_OUT[reg] = 0x8000 #set or unset pin 15
        GPIO_OUT[1] = 0x20 # set clock pin
        GPIO_OUT[2] = 0x20 # unset clock pin

mapping = { "0":0b11101110,
            "1":0b00100010,
            "2":0b10111100,
            "3":0b10110110,
            "4":0b01110010,
            "5":0b11010110,
            "6":0b11011110,
            "7":0b10100010,
            "8":0b11111110,
            "9":0b11110110}

digits = ["1", "3", "3", "7"]

for i in range(4):
    columns[i].on()

sleep_time = 0.00001

def run(sleep_time=sleep_time):
    prev_i = 3
    while True:
        for i, digit in enumerate(digits):
            shiftOut(mapping[digit])
            columns[prev_i].on()
            latch.on()
            columns[i].off()
            sleep(sleep_time)
            prev_i = i

run()
