
import RPi.GPIO as GPIO
import time

# Налаштування GPIO
GPIO.setmode(GPIO.BCM)
pins = {
    "DIR1": 17, "PWM1": 18,   # Переднє ліве
    "DIR2": 22, "PWM2": 23,   # Переднє праве
    "DIR3": 24, "PWM3": 25,   # Заднє ліве
    "DIR4": 5,  "PWM4": 6     # Заднє праве
}

# Ініціалізація пінів
for pin in pins.values():
    GPIO.setup(pin, GPIO.OUT)

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

def move(action, speed=20):
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
    print("Команди: forward, backward, left, right, stop, exit")
    while True:
        cmd = input("Введіть команду: ").strip().lower()
        if cmd == "exit":
            break
        elif cmd in ["forward", "backward", "left", "right", "stop"]:
            move(cmd)
        else:
            print("Невідома команда!")
finally:
    pwm1.stop()
    pwm2.stop()
    pwm3.stop()
    pwm4.stop()
    GPIO.cleanup()
