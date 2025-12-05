import RPi.GPIO as GPIO
import time
import keyboard  # pip install keyboard

GPIO.setmode(GPIO.BCM)

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
# Пины сенсоров
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

# Создаем объекты PWM
pwm1 = GPIO.PWM(pins["PWM1"], 100)
pwm2 = GPIO.PWM(pins["PWM2"], 100)
pwm3 = GPIO.PWM(pins["PWM3"], 100)
pwm4 = GPIO.PWM(pins["PWM4"], 100)

for p in [pwm1, pwm2, pwm3, pwm4]:
    p.start(0)

# ------------------------------
# Функции движения
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
# Ультразвук
# ------------------------------
def get_distance():
    GPIO.output(TRIG, False)
    time.sleep(0.01)

    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)

    while GPIO.input(ECHO) == 0:
        pulse_start = time.time()

    while GPIO.input(ECHO) == 1:
        pulse_end = time.time()

    duration = pulse_end - pulse_start
    distance = duration * 17150
    return round(distance, 2)

# ------------------------------
# Линия
# ------------------------------
def read_line_sensors():
    left = GPIO.input(LEFT_SENSOR)   # 0 = черная
    right = GPIO.input(RIGHT_SENSOR) # 0 = черная
    return left, right

def follow_line(speed=40):
    left, right = read_line_sensors()

    print(f"Left={left}  Right={right}")

    if left == 0 and right == 0:
        forward(speed)
    elif left == 0 and right == 1:
        left_turn()
    elif left == 1 and right == 0:
        right_turn()
    else:
        stop()

def left_turn(speed=35):
    left(speed)

def right_turn(speed=35):
    right(speed)

# ------------------------------
# Главный цикл
# ------------------------------
print("Управление: W A S D, Q — выход")
try:
    while True:
        if keyboard.is_pressed('w'):
            forward()
        elif keyboard.is_pressed('s'):
            backward()
        elif keyboard.is_pressed('a'):
            left()
        elif keyboard.is_pressed('d'):
            right()
        elif keyboard.is_pressed('l'):  # режим линии
            follow_line()
        else:
            stop()

        dist = get_distance()
        ls, rs = read_line_sensors()
        print(f"Dist: {dist} cm | Left={ls} Right={rs}")

        time.sleep(0.05)

except KeyboardInterrupt:
    pass

finally:
    GPIO.cleanup()
