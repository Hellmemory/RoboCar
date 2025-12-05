
import RPi.GPIO as GPIO
import time
import sys
import tty
import termios

# ==========================================
# 1. КОНФІГУРАЦІЯ ПІНІВ
# ==========================================
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

pins = {
    "DIR1": 17, "PWM1": 18,
    "DIR2": 22, "PWM2": 23,
    "DIR3": 24, "PWM3": 25,
    "DIR4": 5,  "PWM4": 6
}

LEFT_SENSOR = 4
RIGHT_SENSOR = 12

# ==========================================
# 2. ІНІЦІАЛІЗАЦІЯ
# ==========================================
for key in pins:
    GPIO.setup(pins[key], GPIO.OUT)

GPIO.setup(LEFT_SENSOR, GPIO.IN)
GPIO.setup(RIGHT_SENSOR, GPIO.IN)

pwm1 = GPIO.PWM(pins["PWM1"], 1000)
pwm2 = GPIO.PWM(pins["PWM2"], 1000)
pwm3 = GPIO.PWM(pins["PWM3"], 1000)
pwm4 = GPIO.PWM(pins["PWM4"], 1000)

for p in [pwm1, pwm2, pwm3, pwm4]:
    p.start(0)

# ==========================================
# 3. ФУНКЦІЇ РУХУ
# ==========================================
def set_motor(pwm_obj, dir_pin, speed, forward=True):
    GPIO.output(dir_pin, GPIO.HIGH if forward else GPIO.LOW)
    pwm_obj.ChangeDutyCycle(speed)

def stop():
    for p in [pwm1, pwm2, pwm3, pwm4]:
        p.ChangeDutyCycle(0)

def move_forward(speed=40):
    set_motor(pwm1, pins["DIR1"], speed, True)
    set_motor(pwm3, pins["DIR3"], speed, True)
    set_motor(pwm2, pins["DIR2"], speed, True)
    set_motor(pwm4, pins["DIR4"], speed, True)

def move_backward(speed=40):
    set_motor(pwm1, pins["DIR1"], speed, False)
    set_motor(pwm3, pins["DIR3"], speed, False)
    set_motor(pwm2, pins["DIR2"], speed, False)
    set_motor(pwm4, pins["DIR4"], speed, False)

def turn_left(speed=45):
    set_motor(pwm1, pins["DIR1"], speed, False)
    set_motor(pwm3, pins["DIR3"], speed, False)
    set_motor(pwm2, pins["DIR2"], speed, True)
    set_motor(pwm4, pins["DIR4"], speed, True)

def turn_right(speed=45):
    set_motor(pwm1, pins["DIR1"], speed, True)
    set_motor(pwm3, pins["DIR3"], speed, True)
    set_motor(pwm2, pins["DIR2"], speed, False)
    set_motor(pwm4, pins["DIR4"], speed, False)

# ==========================================
# 4. КАЛІБРУВАННЯ СЕНСОРІВ
# ==========================================
def calibrate_sensor(pin, samples=50):
    total = 0
    for _ in range(samples):
        total += GPIO.input(pin)
        time.sleep(0.002)
    return total / samples

print("Калібрування сенсорів...")
left_threshold = calibrate_sensor(LEFT_SENSOR)
right_threshold = calibrate_sensor(RIGHT_SENSOR)
print(f"Пороги: Left={left_threshold:.2f}, Right={right_threshold:.2f}")

# ==========================================
# 5. РЕЖИМ СЛІДУВАННЯ ПО ЛІНІЇ
# ==========================================
def line_follower_loop():
    print("\n--- РЕЖИМ ЛІНІЇ ---")
    print("Натисніть CTRL+C для виходу")
    
    SPEED_FWD = 35
    SPEED_TURN = 45

    try:
        while True:
            l_val = GPIO.input(LEFT_SENSOR)
            r_val = GPIO.input(RIGHT_SENSOR)

            l_black = l_val >= left_threshold
            r_black = r_val >= right_threshold

            if not l_black and not r_black:
                move_forward(SPEED_FWD)
            elif l_black and not r_black:
                turn_left(SPEED_TURN)
            elif not l_black and r_black:
                turn_right(SPEED_TURN)
            else:
                stop()

            time.sleep(0.005)

    except KeyboardInterrupt:
        stop()
        print("\nВихід з режиму лінії.")

# ==========================================
# 6. РУЧНЕ УПРАВЛІННЯ
# ==========================================
def getch():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

def manual_control_loop():
    print("\n--- РУЧНИЙ РЕЖИМ ---")
    print("W - Вперед | S - Назад")
    print("A - Вліво  | D - Вправо")
    print("Пробіл - Стоп | Q - Вихід")
    
    try:
        while True:
            char = getch()
            if char == "w":
                move_forward(60)
            elif char == "s":
                move_backward(60)
            elif char == "a":
                turn_left(50)
            elif char == "d":
                turn_right(50)
            elif char == " ":
                stop()
            elif char == "q":
                stop()
                break
            time.sleep(0.1)
            stop()
    except KeyboardInterrupt:
        stop()

# ==========================================
# 7. ГОЛОВНЕ МЕНЮ
# ==========================================
try:
    while True:
        print("\n=== МЕНЮ РОБОТА ===")
        print("1. Ручне управління (WASD)")
        print("2. Їзда по чорній лінії")
        print("3. Вихід")
        
        choice = input("Виберіть режим (1-3): ")
        
        if choice == "1":
            manual_control_loop()
        elif choice == "2":
            line_follower_loop()
        elif choice == "3":
            print("Вихід...")
            break
        else:
            print("Невірний вибір.")

except Exception as e:
    print(f"Помилка: {e}")

finally:
    stop()
    GPIO.cleanup()
