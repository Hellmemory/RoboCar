import RPi.GPIO as GPIO
import time
import keyboard   # pip install keyboard

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# ------------------------------
# Пины моторов
# ------------------------------
pins = {
    "DIR1": 17, "PWM1": 18,
    "DIR2": 22, "PWM2": 23,
    "DIR3": 24, "PWM3": 25,
    "DIR4": 5,  "PWM4": 6
}

# ------------------------------
# Сенсоры линии и расстояния
# ------------------------------
LEFT_SENSOR = 4
RIGHT_SENSOR = 12

TRIG = 20
ECHO = 21

# ------------------------------
# Настройка GPIO
# ------------------------------
for p in pins.values():
    GPIO.setup(p, GPIO.OUT)

GPIO.setup(LEFT_SENSOR, GPIO.IN)
GPIO.setup(RIGHT_SENSOR, GPIO.IN)

GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)

# ------------------------------
# PWM
# ------------------------------
pwm1 = GPIO.PWM(pins["PWM1"], 100)
pwm2 = GPIO.PWM(pins["PWM2"], 100)
pwm3 = GPIO.PWM(pins["PWM3"], 100)
pwm4 = GPIO.PWM(pins["PWM4"], 100)

for p in [pwm1, pwm2, pwm3, pwm4]:
    p.start(0)

# ------------------------------
# Управление моторами
# ------------------------------
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
    for p in [pwm1, pwm2, pwm3, pwm4]:
        p.ChangeDutyCycle(0)

# ------------------------------
# Надёжная функция дистанции (с таймаутом)
# ------------------------------
def get_distance():
    GPIO.output(TRIG, False)
    time.sleep(0.002)

    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)

    timeout = time.time() + 0.02
    pulse_start = None
    pulse_end = None

    # Ждём начала HIGH сигнала
    while GPIO.input(ECHO) == 0:
        pulse_start = time.time()
        if time.time() > timeout:
            return -1

    timeout = time.time() + 0.02

    # Ждём окончания HIGH сигнала
    while GPIO.input(ECHO) == 1:
        pulse_end = time.time()
        if time.time() > timeout:
            return -1

    if pulse_start is None or pulse_end is None:
        return -1

    duration = pulse_end - pulse_start
    distance = duration * 17150

    return round(distance, 2)

# ------------------------------
# Сенсоры линии
# ------------------------------
def read_line_sensors():
    left = GPIO.input(LEFT_SENSOR)
    right = GPIO.input(RIGHT_SENSOR)
    return left, right

def follow_line(speed=40):
    left, right = read_line_sensors()
    print(f"Line sensors: L={left} R={right}")

    # 0 = черная линия
    if left == 0 and right == 0:
        forward(speed)
    elif left == 0 and right == 1:
        left(speed)
    elif left == 1 and right == 0:
        right(speed)
    else:
        stop()

# ------------------------------
# Главный цикл
# ------------------------------
print("Управление: W A S D | L - следовать линии | Q - выход")

try:
    while True:

        # Клавиши управления
        if keyboard.is_pressed('w'):
            forward()
        elif keyboard.is_pressed('s'):
            backward()
        elif keyboard.is_pressed('a'):
            left()
        elif keyboard.is_pressed('d'):
            right()
        elif keyboard.is_pressed('l'):
            follow_line()
        elif keyboard.is_pressed('q'):
            break
        else:
            stop()

        # Чтение сенсоров
        dist = get_distance()
        ls, rs = read_line_sensors()

        print(f"Dist: {dist} cm | Line L={ls} R={rs}")

        time.sleep(0.05)

except KeyboardInterrupt:
    pass

finally:
    stop()
    GPIO.cleanup()
