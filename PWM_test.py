import RPi.GPIO as GPIO
import time
import sys
import select
import tty
import termios

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# -----------------------------------------
# Пины моторов
# -----------------------------------------
pins = {
    "DIR1": 17, "PWM1": 18,
    "DIR2": 22, "PWM2": 23,
    "DIR3": 24, "PWM3": 25,
    "DIR4": 5,  "PWM4": 6
}

# -----------------------------------------
# Сенсоры
# -----------------------------------------
LEFT_SENSOR = 4
RIGHT_SENSOR = 12
TRIG = 20
ECHO = 21

# -----------------------------------------
# GPIO
# -----------------------------------------
for p in pins.values():
    GPIO.setup(p, GPIO.OUT)

GPIO.setup(LEFT_SENSOR, GPIO.IN)
GPIO.setup(RIGHT_SENSOR, GPIO.IN)
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)

# PWM
pwm1 = GPIO.PWM(pins["PWM1"], 100)
pwm2 = GPIO.PWM(pins["PWM2"], 100)
pwm3 = GPIO.PWM(pins["PWM3"], 100)
pwm4 = GPIO.PWM(pins["PWM4"], 100)

for p in (pwm1, pwm2, pwm3, pwm4):
    p.start(0)

# -----------------------------------------
# Движение
# -----------------------------------------
def set_motor(DIR, PWM, direction, speed):
    GPIO.output(DIR, direction)
    PWM.ChangeDutyCycle(speed)

def forward(speed=60):
    set_motor(pins["DIR1"], pwm1, 1, speed)
    set_motor(pins["DIR2"], pwm2, 1, speed)
    set_motor(pins["DIR3"], pwm3, 1, speed)
    set_motor(pins["DIR4"], pwm4, 1, speed)

def backward(speed=60):
    set_motor(pins["DIR1"], pwm1, 0, speed)
    set_motor(pins["DIR2"], pwm2, 0, speed)
    set_motor(pins["DIR3"], pwm3, 0, speed)
    set_motor(pins["DIR4"], pwm4, 0, speed)

def left(speed=60):
    set_motor(pins["DIR1"], pwm1, 0, speed)
    set_motor(pins["DIR3"], pwm3, 0, speed)
    set_motor(pins["DIR2"], pwm2, 1, speed)
    set_motor(pins["DIR4"], pwm4, 1, speed)

def right(speed=60):
    set_motor(pins["DIR1"], pwm1, 1, speed)
    set_motor(pins["DIR3"], pwm3, 1, speed)
    set_motor(pins["DIR2"], pwm2, 0, speed)
    set_motor(pins["DIR4"], pwm4, 0, speed)

def stop():
    for p in (pwm1, pwm2, pwm3, pwm4):
        p.ChangeDutyCycle(0)

# -----------------------------------------
# Дистанция
# -----------------------------------------
def get_distance():
    GPIO.output(TRIG, False)
    time.sleep(0.002)

    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)

    timeout = time.time() + 0.02
    pulse_start = None
    pulse_end = None

    while GPIO.input(ECHO) == 0:
        pulse_start = time.time()
        if time.time() > timeout:
            return -1

    timeout = time.time() + 0.02

    while GPIO.input(ECHO) == 1:
        pulse_end = time.time()
        if time.time() > timeout:
            return -1

    if pulse_start is None or pulse_end is None:
        return -1

    duration = pulse_end - pulse_start
    return round(duration * 17150, 2)

# -----------------------------------------
# Сенсоры линии
# -----------------------------------------
def read_line():
    return GPIO.input(LEFT_SENSOR), GPIO.input(RIGHT_SENSOR)

def follow_line(speed=40):
    L, R = read_line()
    if L == 0 and R == 0:
        forward(speed)
    elif L == 0 and R == 1:
        left(speed)
    elif L == 1 and R == 0:
        right(speed)
    else:
        stop()

# -----------------------------------------
# Чтение клавиш в терминале
# -----------------------------------------
def get_key():
    dr, _, _ = select.select([sys.stdin], [], [], 0)
    if dr:
        return sys.stdin.read(1)
    return None

old_settings = termios.tcgetattr(sys.stdin)
tty.setcbreak(sys.stdin.fileno())

# -----------------------------------------
# Главный цикл
# -----------------------------------------
print("Управление: W A S D | L - линия | Q - выход")

try:
    while True:

        key = get_key()

        if key:
            key = key.lower()

            if key == "w":
                forward()
            elif key == "s":
                backward()
            elif key == "a":
                left()
            elif key == "d":
                right()
            elif key == "l":
                follow_line()
            elif key == "q":
                break
            else:
                stop()
        else:
            stop()

        dist = get_distance()
        L, R = read_line()
        print(f"Dist: {dist}cm | Line L={L} R={R}")

        time.sleep(0.05)

finally:
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
    stop()
    GPIO.cleanup()
