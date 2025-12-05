import RPi.GPIO as GPIO
import time
import curses

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
# curses — быстрый обработчик клавиш
# ================================
def main(stdscr):
    stdscr.nodelay(True)
    stdscr.clear()
    stdscr.addstr(0, 0, "Управление: W A S D | Q — выход")

    while True:
        key = stdscr.getch()

        left = 0
        right = 0

        if key == ord("q"):
            break

        # Получаем ВСЕ нажатые клавиши
        keys = curses.getsyx()  # фактически игнорируется, просто костыль
        key = stdscr.getch()

        # Лучше проверять через stdscr.getch многократно
        pressed = []

        # Проверяем все возможные клавиши (быстро очень)
        for k in (ord('w'), ord('s'), ord('a'), ord('d')):
            if stdscr.getch() == k:
                pressed.append(chr(k))

        # Вперёд
        if 'w' in pressed:
            left += 60
            right += 60

        # Назад
        if 's' in pressed:
            left -= 60
            right -= 60

        # Влево
        if 'a' in pressed:
            left -= 20
            right += 20

        # Вправо
        if 'd' in pressed:
            left += 20
            right -= 20

        # Ограничение
        left = max(-100, min(100, left))
        right = max(-100, min(100, right))

        drive(left, right)
        time.sleep(0.03)

try:
    curses.wrapper(main)
finally:
    stop_all()
    GPIO.cleanup()
