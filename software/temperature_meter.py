from onewire import OneWire, OneWireError
from ds18x20 import DS18X20
from machine import Pin
from time import sleep
import network
import machine

wlan = network.WLAN(network.AP_IF)
wlan.active(True)
wlan.config(essid="\U0001F4A9", password="atpisies1337")

columns = [Pin(16, Pin.OUT), Pin(14, Pin.OUT), Pin(12, Pin.OUT), Pin(13, Pin.OUT)]

clock = Pin(5, Pin.OUT)
latch = Pin(4, Pin.OUT)
data = Pin(15, Pin.OUT)

ds = DS18X20(OneWire(Pin(2)))
sensors = []

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
            "9":0b11110110,
            " ":0b00000000,
            "e":0b11011100, #Actually, an E
            "r":0b00011000,
            "-":0b00010000,
            "_":0b00000100,
            "=":0b10000000, #Actually, it's a storm^W^W upper line
            ".":0b00000001}

#Bootup things
for i in range(4):
    columns[i].on()
thermometers = ds.scan()

current_thermometer = 0

is_error = False
digits = ["1", "3", "3", "7"]
digit_bytes = [mapping[digit] for digit in digits]

temperatures = [None, None]

def generate_digit_bytes(temp_str, thermometer_addr):
    print(thermometer_addr)
    if temp_str[0] == "-":
        temp_str = temp_str[1:]
        negative = True
    else:
        negative = False
    if len(temp_str) > 4:
        raise ValueError("Invalid temp str - {}! Is it so fucking hot?".format(temp_str))
    digit_bytes = [0 for i in range(len(temp_str))]
    if negative:
        digit_bytes[0] = mapping["-"]
    #I'm so hardcode
    if thermometer_addr == b'(\x04\xcf[\x05\x00\x00\xf6':
        #Outside thermometer
        digit_bytes[0] = digit_bytes[0] | mapping["="] #Again, = stands for upper line 
    elif thermometer_addr == b'(\x1fu[\x05\x00\x00\xa7':
        #Inside thermometer
        digit_bytes[0] = digit_bytes[0] | mapping["_"]
    i = 0
    for char in temp_str:
        if char == ".":
            digit_bytes[i] = digit_bytes[i] | mapping["."]
        else:
            i += 1
            digit_bytes[i] = mapping[char]
    #print([bin(byte) for byte in digit_bytes])
    return digit_bytes

def run(sleep_time=0.0001, cycle_counter=50000, update_counter=10000, format_counter=10010, trigger_counter=5000):
    #Good luck understanding this lol
    global thermometers, current_thermometer, is_error, digit_bytes
    print("Hello!")
    prev_i = 3
    run_counter = 0
    while True:
        for i, digit_byte in enumerate(digit_bytes):
            isr = machine.disable_irq()
            shiftOut(digit_byte)
            columns[prev_i].on()
            latch.on()
            columns[i].off()
            machine.enable_irq(isr)
            run_counter += 1
            if run_counter >= cycle_counter:
               print("cycling through thermometers")
               current_thermometer += 1
               if current_thermometer >= len(thermometers):
                   current_thermometer = 0
               print("current thermometer: {}".format(current_thermometer))
               run_counter = 0
            elif run_counter % update_counter == 0:
               print("getting temperature")
               try:
                   temperature = ds.read_temp(thermometers[current_thermometer])
               except OneWireError:
                   print("sensor {} failed".format(thermometer))
                   is_error = True
               else:
                   temperatures[current_thermometer] = temperature
               if is_error:
                   thermometers = ds.scan()
                   if not thermometers:
                       print("No sensors found!")
                       digit_bytes = [mapping[char] for char in " err"]
                   else:
                       is_error = False
            elif run_counter % format_counter == 0 and not is_error:
               print("formatting temperatures for display")
               temp_str = "{:.1f}".format(temperatures[current_thermometer])
               print("sensor {} has temperature {}".format(current_thermometer, temp_str))
               digit_bytes = generate_digit_bytes(temp_str, thermometers[current_thermometer])
            elif run_counter % trigger_counter == 0:
               print("updating temperatures")
               ds.convert_temp()

            sleep(sleep_time)
            prev_i = i

run()
