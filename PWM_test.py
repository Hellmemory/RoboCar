
import RPi.GPIO as GPIO
import time

# Налаштування GPIO
GPIO.setmode(GPIO.BCM)
pins = {
    "DIR1": 17, "PWM1": 18,   # Переднє ліве аааа
    "DIR2": 22, "PWM2": 23,   # Переднє праве
    "DIR3": 24, "PWM3": 25,   # Заднє ліве
    "DIR4": 5,  "PWM4": 6     # Заднє праве
}

# Сенсори
LEFT_SENSOR = 4
RIGHT_SENSOR = 12

# Налаштування моторів
for pin in pins.values():
    GPIO.setup(pin, GPIO.OUT)

# Налаштування сенсорів
GPIO.setup(LEFT_SENSOR, GPIO.IN)
GPIO.setup(RIGHT_SENSOR, GPIO.IN)

# PWM для кожного колеса
pwm1 = GPIO.PWM(pins["PWM1"], 100)
pwm2 = GPIO.PWM(pins["PWM2"], 100)
pwm3 = GPIO.PWM(pins["PWM3"], 100)
pwm4 = GPIO.PWM(pins["PWM4"], 100)

for pwm in [pwm1, pwm2, pwm3, pwm4]:
    pwm.start(0)

def set_motor(dir_pin, pwm_obj, direction, speed):
    GPIO.output(dir_pin, direction)
    pwm_obj.ChangeDutyCycle(speed)

def move(action, speed=45):  # Зменшена швидкість
    if action == "forward":
        set_motor(pins["DIR1"], pwm1, True, speed)
        set_motor(pins["DIR2"], pwm2, True, speed)
        set_motor(pins["DIR3"], pwm3, True, speed)
        set_motor(pins["DIR4"], pwm4, True, speed)
    elif action == "backward":
        set_motor(pins["DIR1"], pwm1, False, speed)
        set_motor(pins["DIR2"], pwm2, False, speed)
        set_motor(pins["DIR3"], pwm3, False, speed)
        set_motor(pins["DIR4"], pwm4, False, speed)
    elif action == "left":
        set_motor(pins["DIR1"], pwm1, False, speed)
        set_motor(pins["DIR2"], pwm2, True, speed)
        set_motor(pins["DIR3"], pwm3, False, speed)
        set_motor(pins["DIR4"], pwm4, True, speed)
    elif action == "right":
        set_motor(pins["DIR1"], pwm1, True, speed)
        set_motor(pins["DIR2"], pwm2, False, speed)
        set_motor(pins["DIR3"], pwm3, True, speed)
        set_motor(pins["DIR4"], pwm4, False, speed)
    elif action == "stop":
        for pwm in [pwm1, pwm2, pwm3, pwm4]:
            pwm.ChangeDutyCycle(0)

try:
    print("Керування: W-вперед, S-назад, A-вліво, D-вправо, X-стоп, Q-вихід")
    while True:
        # Читання сенсорів
        left = GPIO.input(LEFT_SENSOR)
        right = GPIO.input(RIGHT_SENSOR)
        print(f"Left: {'BLACK' if left == 0 else 'WHITE'} | Right: {'BLACK' if right == 0 else 'WHITE'}")

        cmd = input("Введіть команду: ").strip().lower()
        if cmd == "w":
            move("forward")
        elif cmd == "s":
            move("backward")
        elif cmd == "a":
            move("left")
        elif cmd == "d":
            move("right")
        elif cmd == "x":
            move("stop")
        elif cmd == "q":
            print("Вихід...")
            break
        else:
            print("Невідома команда!")
finally:
    pwm1.stop()
    pwm2.stop()
    pwm3.stop()
    pwm4.stop()
    GPIO.cleanup()
