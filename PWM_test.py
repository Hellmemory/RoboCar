
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

def move(action, speed=50):
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

# Функція для неблокуючого читання клавіш
def get_key():
    dr, dw, de = select.select([sys.stdin], [], [], 0)
    if dr:
        return sys.stdin.read(1)
  
old_settings = termios.tcgetattr(sys.stdin)
tty.setcbreak(sys.stdin.fileno())

try:
    print("Ручний режим: W/S/A/D для руху, X - стоп, Q - вихід, +/- змінити швидкість")
    speed = 50
    while True:
        key = get_key()

        # Читаємо сенсори
        left = GPIO.input(LEFT_SENSOR)
        right = GPIO.input(RIGHT_SENSOR)
        dist = get_distance()
        print(f"Left: {'BLACK' if left == 1 else 'WHITE'} | Right: {'BLACK' if right == 1 else 'WHITE'} | Distance: {dist:.1f} cm | Speed: {speed}")

        if key:
            if key.lower() == "w":
                move("forward", speed)
            elif key.lower() == "s":
                move("backward", speed)
            elif key.lower() == "a":
                move("left", speed)
            elif key.lower() == "d":
                move("right", speed)
            elif key.lower() == "x":
                move("stop")
            elif key.lower() == "q":
                print("Вихід...")
                break
            elif key == "+":
                speed = min(100, speed + 10)
            elif key == "-":
                speed = max(10, speed - 10)
        else:
            move("stop")  # Якщо нічого не натиснуто

        time.sleep(0.05)

finally:
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
    move("stop")
