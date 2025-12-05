import RPi.GPIO as GPIO
import time
import sys
import tty
import termios

# ==========================================
# 1. КОНФИГУРАЦИЯ ПИНОВ (Ваши данные)
# ==========================================

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Пины моторов
pins = {
    "DIR1": 17, "PWM1": 18,   # Переднее левое
    "DIR2": 22, "PWM2": 23,   # Переднее правое
    "DIR3": 24, "PWM3": 25,   # Заднее левое
    "DIR4": 5,  "PWM4": 6     # Заднее правое
}

# Пины сенсоров линии
LEFT_SENSOR = 4
RIGHT_SENSOR = 12

# ==========================================
# 2. ИНИЦИАЛИЗАЦИЯ
# ==========================================

# Моторы
for key in pins:
    GPIO.setup(pins[key], GPIO.OUT)

# Сенсоры
GPIO.setup(LEFT_SENSOR, GPIO.IN)
GPIO.setup(RIGHT_SENSOR, GPIO.IN)

# ШИМ (Скорость)
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
    set_motor(pwm1, pins["DIR1"], speed, True)  # FL
    set_motor(pwm3, pins["DIR3"], speed, True)  # RL
    set_motor(pwm2, pins["DIR2"], speed, True)  # FR
    set_motor(pwm4, pins["DIR4"], speed, True)  # RR

def move_backward(speed=40):
    set_motor(pwm1, pins["DIR1"], speed, False)
    set_motor(pwm3, pins["DIR3"], speed, False)
    set_motor(pwm2, pins["DIR2"], speed, False)
    set_motor(pwm4, pins["DIR4"], speed, False)

def turn_left(speed=45):
    # Левые назад, Правые вперед
    set_motor(pwm1, pins["DIR1"], speed, False)
    set_motor(pwm3, pins["DIR3"], speed, False)
    set_motor(pwm2, pins["DIR2"], speed, True)
    set_motor(pwm4, pins["DIR4"], speed, True)

def turn_right(speed=45):
    # Левые вперед, Правые назад
    set_motor(pwm1, pins["DIR1"], speed, True)
    set_motor(pwm3, pins["DIR3"], speed, True)
    set_motor(pwm2, pins["DIR2"], speed, False)
    set_motor(pwm4, pins["DIR4"], speed, False)

# ==========================================
# 4. ЛОГИКА СЕНСОРОВ ЛИНИИ
# ==========================================

def line_follower_loop():
    print("\n--- ЗАПУСК ПО ЛИНИИ ---")
    print("Нажмите CTRL+C для остановки")
    
    # Скорость для линии (обычно ниже, чем для гонок)
    SPEED_FWD = 35
    SPEED_TURN = 45 

    try:
        while True:
            # Читаем датчики (0 - белое, 1 - черное)
            # ПРИМЕЧАНИЕ: На некоторых датчиках наоборот.
            # Если не работает, поменяйте 0 и 1 местами в условиях ниже.
            l_val = GPIO.input(LEFT_SENSOR)
            r_val = GPIO.input(RIGHT_SENSOR)

            # 1. Оба видят белое (линия посередине) -> Едем прямо
            if l_val == 0 and r_val == 0:
                move_forward(SPEED_FWD)

            # 2. Левый видит черное (уходим вправо) -> Поворот влево
            elif l_val == 1 and r_val == 0:
                turn_left(SPEED_TURN)

            # 3. Правый видит черное (уходим влево) -> Поворот вправо
            elif l_val == 0 and r_val == 1:
                turn_right(SPEED_TURN)

            # 4. Оба видят черное (перекресток или финиш) -> Стоп
            elif l_val == 1 and r_val == 1:
                stop()
            
            time.sleep(0.01) # Маленькая пауза для стабильности

    except KeyboardInterrupt:
        stop()
        print("\nОстановка режима линии.")

# ==========================================
# 5. РУЧНОЕ УПРАВЛЕНИЕ (Чтение клавиш)
# ==========================================

def getch():
    """Считывает нажатие клавиши без Enter"""
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

def manual_control_loop():
    print("\n--- РУЧНОЕ УПРАВЛЕНИЕ ---")
    print("W - Вперед | S - Назад")
    print("A - Влево  | D - Вправо")
    print("Пробел - Стоп | Q - Выход в меню")
    
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
            
            # Короткий импульс движения, чтобы робот не ехал бесконечно
            # Если хотите, чтобы он ехал пока держите, логика сложнее
            time.sleep(0.1) 
            stop()

    except KeyboardInterrupt:
        stop()

# ==========================================
# 6. ГЛАВНОЕ МЕНЮ
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