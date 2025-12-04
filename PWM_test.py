
import RPi.GPIO as GPIO
import time
import sys
import termios
import tty
import select

GPIO.setmode(GPIO.BCM)

# Піни для моторів
pins = {
    "DIR1": 17, "PWM1": 18,  # Ліве переднє
    "DIR2": 22, "PWM2": 23,  # Ліве заднє
    "DIR3": 24, "PWM3": 25,  # Праве переднє
    "DIR4": 5,  "PWM4": 6    # Праве заднє
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

        while key:
            keys_pressed.append(key.lower())
            key = get_key()

        # Читаємо сенсори
        left = GPIO.input(LEFT_SENSOR)
        right = GPIO.input(RIGHT_SENSOR)
        dist = get_distance()
        print(f"Left: {'BLACK' if left else 'WHITE'} | Right: {'BLACK' if right else 'WHITE'} | Distance: {dist:.1f} cm")

        if "q" in keys_pressed:
            print("Вихід...")
            break

        if "x" in keys_pressed or not keys_pressed:
            stop_all()
        else:
            forward_speed = 50
            turn_speed = 90

            # Визначаємо напрямок
            if "w" in keys_pressed:  # вперед
                direction = True
            elif "s" in keys_pressed:  # назад
                direction = False
            else:
                direction = None

            if direction is not None:
                # Базовий рух
                left_speed = forward_speed
                right_speed = forward_speed

                # Корекція для повороту
                if "a" in keys_pressed:  # вліво
                    left_speed = forward_speed
                    right_speed = turn_speed
                elif "d" in keys_pressed:  # вправо
                    left_speed = turn_speed
                    right_speed = forward_speed

                # Застосовуємо швидкості
                set_motor(pins["DIR1"], pwm1, direction, left_speed)
                set_motor(pins["DIR2"], pwm2, direction, left_speed)
                set_motor(pins["DIR3"], pwm3, direction, right_speed)
                set_motor(pins["DIR4"], pwm4, direction, right_speed)
            else:
                # Якщо тільки A або D (чистий поворот на місці)
                if "a" in keys_pressed:
                    set_motor(pins["DIR1"], pwm1, False, turn_speed)
                    set_motor(pins["DIR2"], pwm2, False, turn_speed)
                    set_motor(pins["DIR3"], pwm3, True, turn_speed)
                    set_motor(pins["DIR4"], pwm4, True, turn_speed)
                elif "d" in keys_pressed:
                    set_motor(pins["DIR1"], pwm1, True, turn_speed)
                    set_motor(pins["DIR2"], pwm2, True, turn_speed)
                    set_motor(pins["DIR3"], pwm3, False, turn_speed)
                    set_motor(pins["DIR4"], pwm4, False, turn_speed)

        time.sleep(0.05)

finally:
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
    stop_all()
