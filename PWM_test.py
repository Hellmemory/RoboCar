
import RPi.GPIO as GPIO
import time
import sys
import tty
import termios

# ==========================================
# 1. КОНФИГУРАЦИЯ ПИНОВ
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
# 2. ИНИЦИАЛИЗАЦИЯ
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
# 3. ФУНКЦИИ ДВИЖЕНИЯ
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
# 4. КАЛИБРОВКА СЕНСОРОВ
# ==========================================
def calibrate_sensor(pin, samples=50):
    total = 0
    for _ in range(samples):
        total += GPIO.input(pin)
        time.sleep(0.002)
    return total / samples

print("Калибровка сенсоров...")
left_threshold = calibrate_sensor(LEFT_SENSOR)
right_threshold = calibrate_sensor(RIGHT_SENSOR)
print(f"Пороги: Left={left_threshold:.2f}, Right={right_threshold:.2f}")

# ==========================================
# 5. ЛОГИКА СЕНСОРОВ ЛИНИИ
# ==========================================
def line_follower_loop():
    print("\n--- ЗАПУСК ПО ЛИНИИ ---")
    print("Нажмите CTRL+C для остановки")
    
    SPEED_FWD = 35
    SPEED_TURN = 45

    try:
        while True:
            l_val = GPIO.input(LEFT_SENSOR)
            r_val = GPIO.input(RIGHT_SENSOR)

            # Сравнение с порогами
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
        print("\nОстановка режима линии.")

# ==========================================
# 6. РУЧНОЕ УПРАВЛЕНИЕ
#    print("W - Вперед | S - Назад")
    print("A - Влево  | D - Вправо")
    print("Пробел - Стоп | Q - Выход в меню")
    
            elif char == "q":
                stop()
                break
            time.sleep(0.1)
            stop()
    except KeyboardInterrupt:
        stop()

# ==========================================
# 7. МЕНЮ
# ==========================================
try:
    while True:
        print("\n=== МЕНЮ РОБОТА ===")
        print("1. Ручное управление (WASD)")
        print("2. Езда по черной линии")
        print("3. Выход")
        
        choice = input("Выберите режим (1-3): ")
        
        if choice == "1":
            manual_control_loop()
        elif choice == "2":
            line_follower_loop()
        elif choice == "3":
            print("Выход...")
            break
        else:
            print("Неверный ввод.")

except Exception as e:
    print(f"Ошибка: {e}")

finally:
    stop()
    GPIO.cleanup()
