from machine import Pin
from time import sleep, time
import network
import machine

wlan = network.WLAN(network.AP_IF)
wlan.active(True)
wlan.config(essid="\U0001F4A9", password="atpisies1337")

stawlan = network.WLAN(network.STA_IF)
stawlan.active(False)

columns = [Pin(16, Pin.OUT), Pin(14, Pin.OUT), Pin(12, Pin.OUT), Pin(13, Pin.OUT)]

clock = Pin(5, Pin.OUT)
latch = Pin(4, Pin.OUT)
data = Pin(15, Pin.OUT)

countdown_minutes = 80

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

is_error = False
digits = ["1", "3", "3", "7"]
digit_bytes = [mapping[digit] for digit in digits]

temperatures = [None, None]

def generate_digit_bytes(minutes, seconds):
    # Ran out? Just show "00.00"
    if minutes < 0 or seconds < 0:
        m = [mapping["0"] for i in (1, 2, 3, 4)]
        m[1] = m[1] | mapping['.']
        return m
    # else, build the list of bytes to shift out
    m = [0 for i in range(4)]
    m_s = str(minutes)
    if len(m_s) > 1:
        m[0] = mapping[m_s[0]]
        m[1] = mapping[m_s[1]]
    else:
        m[0] = mapping['0']
        m[1] = mapping[m_s[0]]
    s_s = str(seconds)
    if len(s_s) > 1:
        m[2] = mapping[s_s[0]]
        m[3] = mapping[s_s[1]]
    else:
        m[2] = mapping['0']
        m[3] = mapping[s_s[0]]
    #print([bin(byte) for byte in digit_bytes])
    m[1] = m[1] | mapping['.']
    return m

# 1) get time
# 2) format time
# 3) check button

minutes = 0
seconds = 0

def run(sleep_time=0.0001, tupdate_counter = 1500, tformat_counter = 4000, button_counter = 100):
    global minutes, seconds
    print("Hello!")
    prev_i = 3
    run_counter = 0
    digit_bytes = generate_digit_bytes(minutes, seconds)
    dbl = list(enumerate(digit_bytes))
    while True:
        for i, digit_byte in dbl:
            #isr = machine.disable_irq()
            shiftOut(digit_byte)
            columns[prev_i].on()
            latch.on()
            columns[i].off()
            #machine.enable_irq(isr)
            run_counter += 1
            if run_counter >= tformat_counter:
               print("formatting time")
               digit_bytes = generate_digit_bytes(minutes, seconds)
               dbl = list(enumerate(digit_bytes))
               run_counter = 0
            elif run_counter % tupdate_counter == 0:
               print("getting time")
               t = time()
               diff = t - start_time
               remainder = total_seconds - diff
               minutes, seconds = divmod(remainder, 60)
            if sleep_time:
                sleep(sleep_time)
            prev_i = i

total_seconds = countdown_minutes * 60

start_time = time()
run()
