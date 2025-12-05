import RPi.GPIO as GPIO
import time
import curses

# Настройка GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# ================================
# Моторы
# ================================
pins = {
    "DIR1": 17, "PWM1": 18,   # Переднее левое
    "DIR2": 22, "PWM2": 23,   # Переднее правое
    "DIR3": 24, "PWM3": 25,   # Заднее левое
    "DIR4": 5,  "PWM4": 6     # Заднее правое
}

for p in pins.values():
    GPIO.setup(p, GPIO.OUT)

pwm1 = GPIO.PWM(pins["PWM1"], 100)
pwm2 = GPIO.PWM(pins["PWM2"], 100)
pwm3 = GPIO.PWM(pins["PWM3"], 100)
pwm4 = GPIO.PWM(pins["PWM4"], 100)

for p in (pwm1, pwm2, pwm3, pwm4):
    p.start(0)

# ================================
# Функции управления
# ================================
def set_motor(DIR, PWM, direction, speed):
    GPIO.output(DIR, direction)
    PWM.ChangeDutyCycle(speed)

def drive(left_speed, right_speed):
    # Левая сторона
    if left_speed >= 0:
        set_motor(pins["DIR1"], pwm1, 1, left_speed)
        set_motor(pins["DIR3"], pwm3, 1, left_speed)
    else:
        set_motor(pins["DIR1"], pwm1, 0, -left_speed)
        set_motor(pins["DIR3"], pwm3, 0, -left_speed)

    # Правая сторона
    if right_speed >= 0:
        set_motor(pins["DIR2"], pwm2, 1, right_speed)
        set_motor(pins["DIR4"], pwm4, 1, right_speed)
    else:
        set_motor(pins["DIR2"], pwm2, 0, -right_speed)
        set_motor(pins["DIR4"], pwm4, 0, -right_speed)

def stop_all():
    for p in (pwm1, pwm2, pwm3, pwm4):
        p.ChangeDutyCycle(0)

# ================================
# Основной цикл
# ================================
def main(stdscr):
    # Настройки curses
    stdscr.nodelay(True)  # Не блокировать программу, если нет нажатия
    stdscr.clear()
    stdscr.addstr(0, 0, "Управление: W A S D | Q — выход")

    speed_val = 60  # Базовая скорость

    while True:
        # Читаем клавишу ОДИН раз
        key = stdscr.getch()

        if key == ord("q"):
            break

        left = 0
        right = 0

        # Проверяем, какая клавиша была нажата (если нажата)
        if key == ord('w'):       # Вперед
            left = speed_val
            right = speed_val
        elif key == ord('s'):     # Назад
            left = -speed_val
            right = -speed_val
        elif key == ord('a'):     # Влево (разворот на месте)
            left = -speed_val
            right = speed_val
        elif key == ord('d'):     # Вправо (разворот на месте)
            left = speed_val
            right = -speed_val
        else:
            # Если ничего не нажато (key == -1), машина останавливается
            left = 0
            right = 0

        drive(left, right)
        time.sleep(0.05) # Небольшая задержка, чтобы не грузить процессор

try:
    curses.wrapper(main)
finally:
    stop_all()
    GPIO.cleanup()