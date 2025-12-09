import time

from machine import PWM, Pin

# --- SAFETY START ---
# Blink the onboard LED (Pin 2) to prove code is running
led = Pin(2, Pin.OUT)
for i in range(3):
    led.value(1)
    time.sleep(0.2)
    led.value(0)
    time.sleep(0.2)

# --- SETUP ---

# Front Motors (Channel A) - ENABLE on D13
enable_front = PWM(Pin(13))
enable_front.freq(1000)
# MOVED D12 -> D33 because D12 blocks booting!
in_front_1 = Pin(33, Pin.OUT)
in_front_2 = Pin(14, Pin.OUT)

# Back Motors (Channel B) - ENABLE on D25
enable_back = PWM(Pin(25))
enable_back.freq(1000)
in_back_1 = Pin(27, Pin.OUT)
in_back_2 = Pin(26, Pin.OUT)


def move_all_motors(speed_percent):
    duty = int((speed_percent / 100) * 65535)
    enable_front.duty_u16(duty)
    enable_back.duty_u16(duty)

    # Front Direction
    in_front_1.value(1)
    in_front_2.value(0)

    # Back Direction
    in_back_1.value(1)
    in_back_2.value(0)


# --- LOOP ---
while True:
    # Use 100% speed because 4 AA batteries are weak
    move_all_motors(100)
    time.sleep(1)
