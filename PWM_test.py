
import RPi.GPIO as GPIO
import time
import sys
import termios
import tty
import select

GPIO.setmode(GPIO.BCM)

# Піни для моторів
pins = {
    "DIR1": 17, "PWM1": 18,   # Переднє ліве
    "DIR2": 22, "PWM2": 23,   # Переднє праве
    "DIR3": 24, "PWM3": 25,   # Заднє ліве
    "DIR4": 5,  "PWM4": 6     # Заднє праве
}

# Сенсори
LEFT_SENSOR = 4
RIGHT_SENSOR = 12

# Налаштування пінів
for pin in pins.values():
    GPIO.setup(pin, GPIO.OUT)
GPIO.setup(LEFT_SENSOR, GPIO.IN)
GPIO.setup(RIGHT_SENSOR, GPIO.IN)

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

# Неблокуюче читання клавіш
def get_key():
    dr, dw, de = select.select([sys.stdin], [], [], 0)
    if dr:
        return sys.stdin.read(1)

# Налаштування терміналу
old_settings = termios.tcgetattr(sys.stdin)
tty.setcbreak(sys.stdin.fileno())

try:
    print("Керування: W-вперед, S-назад, A-вліво, D-вправо, X-стоп, Q-вихід")
    while True:
        key = get_key()
        keys_pressed = []

        while key:
            keys_pressed.append(key.lower())
            key = get_key()

        # Читаємо сенсори
        left = GPIO.input(LEFT_SENSOR)
        right = GPIO.input(RIGHT_SENSOR)
        print(f"Left: {'BLACK' if left == 0 else 'WHITE'} | Right: {'BLACK' if right == 0 else 'WHITE'}")

        if "q" in keys_pressed:
            print("Вихід...")
            break

        if "x" in keys_pressed or not keys_pressed:
            stop_all()
        else:
            forward_speed = 50
            turn_speed = 90

            # Напрямок руху
            if "w" in keys_pressed:
                direction = True  # вперед
            elif "s" in keys_pressed:
                direction = False  # назад
            else:
                direction = True  # чистий поворот вперед

            # Базові швидкості
            left_speed = forward_speed
            right_speed = forward_speed

            # Повороти
            if "a" in keys_pressed:  # вліво
                right_speed = turn_speed
            elif "d" in keys_pressed:  # вправо
                left_speed = turn_speed

            # Застосовуємо швидкості (всі колеса в одному напрямку)
            set_motor(pins["DIR1"], pwm1, direction, left_speed)
            set_motor(pins["DIR3"], pwm3, direction, left_speed)
            set_motor(pins["DIR2"], pwm2, direction, right_speed)
            set_motor(pins["DIR4"], pwm4, direction, right_speed)

        time.sleep(0.05)

finally:
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
    stop_all()
    GPIO.cleanup()
