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

def shiftOut(byte):
    latch.off()
    for i in range(8):
        value = byte & 1<<i
        data.value(value)
        clock.on()
        clock.off()

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
