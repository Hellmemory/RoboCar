
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

for pin in pins.values():
    GPIO.setup(pin, GPIO.OUT)

GPIO.setup(LEFT_SENSOR, GPIO.IN)
GPIO.setup(RIGHT_SENSOR, GPIO.IN)

pwm1 = GPIO.PWM(pins["PWM1"], 100)
pwm2 = GPIO.PWM(pins["PWM2"], 100)
pwm3 = GPIO.PWM(pins["PWM3"], 100)
pwm4 = GPIO.PWM(pins["PWM4"], 100)

for pwm in [pwm1, pwm2, pwm3, pwm4]:
    pwm.start(0)

def set_motor(dir_pin, pwm_obj, direction, speed):
    GPIO.output(dir_pin, direction)
    pwm_obj.ChangeDutyCycle(speed)

def move(left_speed, right_speed):
    # Ліві колеса
    set_motor(pins["DIR1"], pwm1, True, left_speed)
    set_motor(pins["DIR3"], pwm3, True, left_speed)
    # Праві колеса
    set_motor(pins["DIR2"], pwm2, True, right_speed)
    set_motor(pins["DIR4"], pwm4, True, right_speed)

def stop():
    for pwm in [pwm1, pwm2, pwm3, pwm4]:
        pwm.ChangeDutyCycle(0)

try:
    print("Автономний режим: плавне слідування по чорній лінії")
    while True:
        left = GPIO.input(LEFT_SENSOR)
        right = GPIO.input(RIGHT_SENSOR)

        print(f"Left: {'BLACK' if left == 0 else 'WHITE'} | Right: {'BLACK' if right == 0 else 'WHITE'}")

        if left == 0 and right == 0:
            # Обидва на чорному → прямо
            move(50, 50)
        elif left == 0 and right == 1:
            # Лівий чорний → плавно вліво
            move(70, 30)
        elif left == 1 and right == 0:
            # Правий чорний → плавно вправо
            move(30, 70)
        else:
            # Обидва білі → зупинка
            stop()

        time.sleep(0.1)

finally:
    stop()
    GPIO.cleanup()
