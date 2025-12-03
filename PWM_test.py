
import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
pins = {
    "DIR1": 17, "PWM1": 18,
    "DIR2": 22, "PWM2": 23,
    "DIR3": 24, "PWM3": 25,
    "DIR4": 5,  "PWM4": 6
}

LEFT_SENSOR = 4
RIGHT_SENSOR = 12

# Налаштування моторів
for pin in pins.values():
    GPIO.setup(pin, GPIO.OUT)

# Сенсори
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
    GPIO.output(dir_pin, direction)
    pwm_obj.ChangeDutyCycle(speed)

def move(action, speed=50):
    if action == "forward":
        set_motor(pins["DIR1"], pwm1, True, speed)
        set_motor(pins["DIR2"], pwm2, True, speed)
        set_motor(pins["DIR3"], pwm3, True, speed)
        set_motor(pins["DIR4"], pwm4, True, speed)
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
    print("Following black line")
    while True:
        left = GPIO.input(LEFT_SENSOR)
        right = GPIO.input(RIGHT_SENSOR)

        # Логіка: реагує тільки на чорний (0)
        if left == 0 and right == 0:
            move("forward")
        elif left == 0 and right == 1:
            move("left")
        elif left == 1 and right == 0:
            move("right")
        else:
            move("stop")

        time.sleep(0.1)

finally:
    pwm1.stop()
    pwm2.stop()
    pwm3.stop()
    pwm4.stop()
    GPIO.cleanup()
