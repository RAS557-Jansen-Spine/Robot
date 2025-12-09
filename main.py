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


import struct

from machine import I2C

# --- IMU SETUP (BNO055) ---
ADDR = 0x28
I2C_FREQ = 100000
MODE = 0x08  # IMU mode


def _init_i2c():
    try:
        return I2C(0, scl=Pin(22), sda=Pin(21), freq=I2C_FREQ)
    except:
        return I2C(1, scl=Pin(22), sda=Pin(21), freq=I2C_FREQ)


def rb(i2c, reg, n=1):
    return i2c.readfrom_mem(ADDR, reg, n)


def wb(i2c, reg, v):
    i2c.writeto_mem(ADDR, reg, bytes([v & 0xFF]))


def set_mode(i2c, m):
    wb(i2c, 0x3D, m)
    time.sleep_ms(100)


def read_euler_deg(i2c):
    data = rb(i2c, 0x1A, 6)
    h, r, p = struct.unpack("<hhh", data)
    return (h / 16.0, r / 16.0, p / 16.0)


# --- LOOP ---
# Initialize IMU
print("# Initializing IMU...")
try:
    i2c = _init_i2c()
    set_mode(i2c, MODE)
    print("# IMU Ready.")
except Exception as e:
    print(f"# IMU Failed: {e}")
    i2c = None

print("# t_ms,heading,roll,pitch")
t0 = time.ticks_ms()

while True:
    # 1. Drive Motors
    move_all_motors(100)

    # 2. Read IMU
    h, r, p = 0.0, 0.0, 0.0
    if i2c:
        try:
            h, r, p = read_euler_deg(i2c)
        except:
            pass

    # 3. Stream Data
    t = time.ticks_diff(time.ticks_ms(), t0)
    print(f"{t},{h:.2f},{r:.2f},{p:.2f}")

    time.sleep_ms(100)
