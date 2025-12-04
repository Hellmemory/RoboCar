
import RPi.GPIO as GPIO
import time
import sys
import termios
import tty
import select

GPIO.setmode(GPIO.BCM)

# Піни для моторів
pins = {
    "DIR1": 17, "PWM1": 18,
    "DIR2": 22, "PWM2": 23,
    "DIR3": 24, "PWM3": 25,
    "DIR4": 5,  "PWM4": 6
}

# Сенсори
LEFT_SENSOR = 4
RIGHT_SENSOR = 12
TRIG = 20
ECHO = 21

# Налаштування пінів
for pin in pins.values():
    GPIO.setup(pin, GPIO.OUT)
GPIO.setup(LEFT_SENSOR, GPIO.IN)
GPIO.setup(RIGHT_SENSOR, GPIO.IN)
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)

# PWM
pwm1 = GPIO.PWM(pins["PWM1"], 100)
pwm2 = GPIO.PWM(pins["PWM2"], 100)
pwm3 = GPIO.PWM(pins["PWM3"], 100)
pwm4 = GPIO.PWM(pins["PWM4"], 100)

for pwm in [pwm1, pwm2, pwm3, pwm4]:
    pwm.start(0)

def set_motor(dir_pin, pwm_obj, direction, speed):
    GPIO.output(dir_pin, GPIO.HIGH if direction else GPIO.LOW)
    pwm_obj.ChangeDutyCycle(speed)

def stop_all():
    for pwm in [pwm1, pwm2, pwm3, pwm4]:
        pwm.ChangeDutyCycle(0)

def get_distance():
    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)

    start = time.time()
    stop = time.time()

    while GPIO.input(ECHO) == 0:
        start = time.time()
    while GPIO.input(ECHO) == 1:
        stop = time.time()

    elapsed = stop - start
    distance = (elapsed * 34300) / 2
    return distance

# Неблокуюче читання клавіш
def get_key():
    dr, dw, de = select.select([sys.stdin], [], [], 0)
    if dr:
        return sys.stdin.read(1)

# Налаштування терміналу
old_settings = termios.tcgetattr(sys.stdin)
tty.setcbreak(sys.stdin.fileno())

try:
    print("Ручний режим: W/S/A/D для руху, X - стоп, Q - вихід")
    while True:
        key = get_key()
        keys_pressed = []

        # Збираємо всі натиснуті клавіші
        while key:
            keys_pressed.append(key.lower())
            key = get_key()

        # Читаємо сенсори
        left = GPIO.input(LEFT_SENSOR)
        right = GPIO.input(RIGHT_SENSOR)
        dist = get_distance()
        print(f"Left: {'BLACK' if left else 'WHITE'} | Right: {'BLACK' if right else 'WHITE'} | Distance: {dist:.1f} cm")

        # Логіка руху
        if "q" in keys_pressed:
            print("Вихід...")
            break

        if "x" in keys_pressed or not keys_pressed:
            stop_all()
        else:
            forward_speed = 50
            turn_speed = 90

            # Комбінації
            if "w" in keys_pressed and "d" in keys_pressed:  # вперед + вправо
