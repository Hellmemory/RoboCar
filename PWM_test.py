
import RPi.GPIO as GPIO
import time
import keyboard  # Потрібно встановити: pip install keyboard

GPIO.setmode(GPIO.BCM)
pins = {
    "DIR1": 17, "PWM1": 18,
    "DIR2": 22, "PWM2": 23,
    "DIR3": 24, "PWM3": 25,
    "DIR4": 5,  "PWM4": 6
}

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
    GPIO.output(dir_pin, direction)
    pwm_obj.ChangeDutyCycle(speed)

def move(action):
    if action == "forward":
        speed = 50
        set_motor(pins["DIR1"], pwm1, True, speed)
        set_motor(pins["DIR2"], pwm2, True, speed)
        set_motor(pins["DIR3"], pwm3, True, speed)
        set_motor(pins["DIR4"], pwm4, True, speed)
    elif action == "backward":
        speed = 50
        set_motor(pins["DIR1"], pwm1, False, speed)
        set_motor(pins["DIR2"], pwm2, False, speed)
        set_motor(pins["DIR3"], pwm3, False, speed)
        set_motor(pins["DIR4"], pwm4, False, speed)
    elif action == "left":
        speed = 100
        set_motor(pins["DIR1"], pwm1, False, speed)
        set_motor(pins["DIR2"], pwm2, True, speed)
        set_motor(pins["DIR3"], pwm3, False, speed)
        set_motor(pins["DIR4"], pwm4, True, speed)
    elif action == "right":
        speed = 100
        set_motor(pins["DIR1"], pwm1, True, speed)
        set_motor(pins["DIR2"], pwm2, False, speed)
        set_motor(pins["DIR3"], pwm3, True, speed)
        set_motor(pins["DIR4"], pwm4, False, speed)
    elif action == "stop":
        for pwm in [pwm1, pwm2, pwm3, pwm4]:
            pwm.ChangeDutyCycle(0)

def get_distance():
    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)

    start = time.time()
    stop = time.time()

    while GPIOть режим: M - Ручний, A - Автономний: ").strip().lower()

    if mode == "m":
        print("Ручний режим: натискай W/S/A/D, X - стоп, Q - вихід")
        while True:
            if keyboard.is_pressed("w"):
                move("forward")
            elif keyboard.is_pressed("s"):
                move("backward")
            elif keyboard.is_pressed("a"):
                           elif keyboard.is_pressed("q"):
                print("Вихід...")
                break
            else:
                move("stop")  # Якщо нічого не натиснуто
            time.sleep(0.05)

    elif mode == "a":
        print("Автономний режим: їде по чорній лінії, зупиняється на білому або перешкоді")
        while True:
            left = GPIO.input(LEFT_SENSOR)
            right = GPIO.input(RIGHT_SENSOR)
            dist = get_distance()

            print(f"Left: {'BLACK' if left == 1 else 'WHITE'} | Right: {'BLACK' if right == 1 else 'WHITE'} | Distance: {dist:.1f} cm")

            if dist < 20:
                move("stop")
                print("Перешкода! Зупинка.")
            elif left == 1 and right == 1:
                move("forward")
            elif left == 1 and right == 0:
                move("left")
            elif left == 0 and right == 1:
                move("right")
            else:
                move("stop")

            time.sleep(0.1)

finally:
    move("stop")
    GPIO.cleanup()
