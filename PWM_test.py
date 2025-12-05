import RPi.GPIO as GPIO
import time

# ==========================================
# 1. КОНФИГУРАЦИЯ ПИНОВ (Ваши данные)
# ==========================================

# Установка режима нумерации пинов (BCM)
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Пины моторов
pins = {
    "DIR1": 17, "PWM1": 18,   # Переднее левое (Front Left)
    "DIR2": 22, "PWM2": 23,   # Переднее правое (Front Right)
    "DIR3": 24, "PWM3": 25,   # Заднее левое (Rear Left)
    "DIR4": 5,  "PWM4": 6     # Заднее правое (Rear Right)
}

# Пины сенсоров
LEFT_SENSOR = 4
RIGHT_SENSOR = 12
TRIG = 20
ECHO = 21

# ==========================================
# 2. ИНИЦИАЛИЗАЦИЯ (SETUP)
# ==========================================

# Настройка пинов моторов на выход
for key in pins:
    GPIO.setup(pins[key], GPIO.OUT)

# Настройка пинов сенсоров
GPIO.setup(LEFT_SENSOR, GPIO.IN)
GPIO.setup(RIGHT_SENSOR, GPIO.IN)
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)

# Настройка ШИМ (PWM) - частота 1000 Гц
pwm1 = GPIO.PWM(pins["PWM1"], 1000)
pwm2 = GPIO.PWM(pins["PWM2"], 1000)
pwm3 = GPIO.PWM(pins["PWM3"], 1000)
pwm4 = GPIO.PWM(pins["PWM4"], 1000)

# Запуск ШИМ с нулевой скоростью
pwm1.start(0)
pwm2.start(0)
pwm3.start(0)
pwm4.start(0)

# ==========================================
# 3. ФУНКЦИИ ДВИЖЕНИЯ (Как в презентации)
# ==========================================

def set_motor(pwm_obj, dir_pin, speed, forward=True):
    """
    Универсальная функция управления одним мотором.
    speed: 0-100
    forward: True (вперед) или False (назад)
    """
    GPIO.output(dir_pin, GPIO.HIGH if forward else GPIO.LOW)
    pwm_obj.ChangeDutyCycle(speed)

def stop():
    """Остановка всех моторов"""
    pwm1.ChangeDutyCycle(0)
    pwm2.ChangeDutyCycle(0)
    pwm3.ChangeDutyCycle(0)
    pwm4.ChangeDutyCycle(0)
    print("Робот остановлен")

def move_forward(speed=50):
    """Движение вперед всеми 4 колесами"""
    # Левая сторона
    set_motor(pwm1, pins["DIR1"], speed, forward=True) # FL
    set_motor(pwm3, pins["DIR3"], speed, forward=True) # RL
    # Правая сторона
    set_motor(pwm2, pins["DIR2"], speed, forward=True) # FR
    set_motor(pwm4, pins["DIR4"], speed, forward=True) # RR
    print(f"Вперед со скоростью {speed}")

def move_backward(speed=50):
    """Движение назад"""
    # Левая сторона
    set_motor(pwm1, pins["DIR1"], speed, forward=False)
    set_motor(pwm3, pins["DIR3"], speed, forward=False)
    # Правая сторона
    set_motor(pwm2, pins["DIR2"], speed, forward=False)
    set_motor(pwm4, pins["DIR4"], speed, forward=False)
    print(f"Назад со скоростью {speed}")

def turn_left(speed=40):
    """Поворот влево (танковый разворот)"""
    # Левая назад
    set_motor(pwm1, pins["DIR1"], speed, forward=False)
    set_motor(pwm3, pins["DIR3"], speed, forward=False)
    # Правая вперед
    set_motor(pwm2, pins["DIR2"], speed, forward=True)
    set_motor(pwm4, pins["DIR4"], speed, forward=True)
    print("Поворот влево")

def turn_right(speed=40):
    """Поворот вправо (танковый разворот)"""
    # Левая вперед
    set_motor(pwm1, pins["DIR1"], speed, forward=True)
    set_motor(pwm3, pins["DIR3"], speed, forward=True)
    # Правая назад
    set_motor(pwm2, pins["DIR2"], speed, forward=False)
    set_motor(pwm4, pins["DIR4"], speed, forward=False)
    print("Поворот вправо")

# ==========================================
# 4. ФУНКЦИИ СЕНСОРОВ
# ==========================================

def get_distance():
    """Получение дистанции с ультразвукового датчика (см)"""
    GPIO.output(TRIG, False)
    time.sleep(0.05) # Небольшая задержка для стабилизации

    GPIO.output(TRIG, True)
    time.sleep(0.00001) # Импульс 10 мкс
    GPIO.output(TRIG, False)

    pulse_start = time.time()
    pulse_end = time.time()

    # Ждем начала эха (Low -> High)
    timeout = time.time() + 0.1
    while GPIO.input(ECHO) == 0:
        pulse_start = time.time()
        if pulse_start > timeout: return -1

    # Ждем конца эха (High -> Low)
    while GPIO.input(ECHO) == 1:
        pulse_end = time.time()
        if pulse_end > timeout: return -1

    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 17150 # Скорость звука / 2
    return round(distance, 2)

def read_line_sensors():
    """Возвращает кортеж (Left, Right). 0 - белое, 1 - черное (обычно)"""
    left_val = GPIO.input(LEFT_SENSOR)
    right_val = GPIO.input(RIGHT_SENSOR)
    return left_val, right_val

# ==========================================
# 5. ОСНОВНОЙ ЦИКЛ (Тест как в презентации)
# ==========================================

try:
    print("Тест системы запущен...")
    
    # Пример 1: Проверка дистанции
    dist = get_distance()
    print(f"Дистанция до препятствия: {dist} см")
    
    # Пример 2: Движение (логика Day 1.3)
    # Едем вперед 2 секунды
    move_forward(50) 
    time.sleep(2)
    
    # Останавливаемся
    stop()
    time.sleep(1)
    
    # Разворот вправо 1 секунду
    turn_right(60)
    time.sleep(1)
    
    stop()
    
    # Пример 3: Тест датчиков линии
    print("Чтение датчиков линии (Ctrl+C для выхода):")
    while True:
        l, r = read_line_sensors()
        print(f"Line Sensors -> L: {l}, R: {r}")
        time.sleep(0.2)

except KeyboardInterrupt:
    print("\nПрограмма остановлена пользователем")
    stop()
    GPIO.cleanup()
    
except Exception as e:
    print(f"Ошибка: {e}")
    stop()
    GPIO.cleanup()
finally:
    # Всегда очищаем пины при выходе
    stop()
    GPIO.cleanup()