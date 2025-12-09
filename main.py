# main.py
# Unified file for ESP32 Robot Control (Motors + BNO055 IMU)
# Plotting logic moved to live_plot.py

# -------------------------------------------------------------------------
#                            MICROPYTHON (ESP32)
# -------------------------------------------------------------------------
import struct
import time

import machine
from machine import I2C, PWM, Pin


# --- MOTOR CONTROL CLASS ---
class MotorDriver:
    def __init__(self):
        # Front Motors (Channel A) - ENABLE on D13
        self.enable_front = PWM(Pin(13))
        self.enable_front.freq(1000)
        # Pins for Front Direction (Moved D12->D33 for safety)
        self.in_front_1 = Pin(33, Pin.OUT)
        self.in_front_2 = Pin(14, Pin.OUT)

        # Back Motors (Channel B) - ENABLE on D25
        self.enable_back = PWM(Pin(25))
        self.enable_back.freq(1000)
        # Pins for Back Direction
        self.in_back_1 = Pin(27, Pin.OUT)
        self.in_back_2 = Pin(26, Pin.OUT)

    def move(self, speed_percent):
        # Constrain speed
        speed_percent = max(0, min(100, speed_percent))
        duty = int((speed_percent / 100) * 65535)
        self.enable_front.duty_u16(duty)
        self.enable_back.duty_u16(duty)

        # Forward Direction
        self.in_front_1.value(1)
        self.in_front_2.value(0)
        self.in_back_1.value(1)
        self.in_back_2.value(0)

    def stop(self):
        self.enable_front.duty_u16(0)
        self.enable_back.duty_u16(0)
        self.in_front_1.value(0)
        self.in_front_2.value(0)
        self.in_back_1.value(0)
        self.in_back_2.value(0)


# --- BNO055 IMU HELPERS ---
ADDR = 0x28  # BNO055 at 0x28
I2C_FREQ = 100000
MODE = 0x08  # IMU mode (gyro+acc, no magnetometer)
HZ = 10  # Output rate


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
    time.sleep_ms(100)  # 0x3D = OPR_MODE


def read_euler_deg(i2c):
    # 0x1A..0x1F = Euler H, R, P (LSB=1/16 deg)
    data = rb(i2c, 0x1A, 6)
    h, r, p = struct.unpack("<hhh", data)
    return (h / 16.0, r / 16.0, p / 16.0)


# --- MAIN ESP32 LOOP ---
def main_esp32():
    # 1. Setup Motors
    motors = MotorDriver()

    # 2. Setup IMU
    print("# Initializing IMU...")
    try:
        i2c = _init_i2c()
        set_mode(i2c, MODE)
        print("# IMU Ready.")
    except Exception as e:
        print(f"# IMU Init Failed: {e}")
        i2c = None

    print("# t_ms,heading_deg,roll_deg,pitch_deg")

    # 3. Control Loop
    t0 = time.ticks_ms()
    period = int(1000 / HZ)
    last = t0

    # Drive forward immediately
    motors.move(100)

    try:
        while True:
            now = time.ticks_ms()
            # Simple non-blocking rate limiter
            if time.ticks_diff(now, last) < period:
                time.sleep_ms(2)
                continue
            last = now

            # Read IMU
            h, r, p = 0.0, 0.0, 0.0
            if i2c:
                try:
                    h, r, p = read_euler_deg(i2c)
                except:
                    pass  # Ignore I2C errors to keep motors running

            # Stream Data
            t = time.ticks_diff(now, t0)
            print("%d,%.3f,%.3f,%.3f" % (t, h, r, p))

    except KeyboardInterrupt:
        motors.stop()
        print("# Stopped.")


# Run the main loop
main_esp32()
