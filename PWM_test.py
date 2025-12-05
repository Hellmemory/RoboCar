import RPi.GPIO as GPIO
import time
from pynput import keyboard

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
# Логика движения
# ================================
pressed = set()

def set_motor(DIR, PWM, direction, speed):
    GPIO.output(DIR, direction)
    PWM.ChangeDutyCycle(speed)

def drive():
    # Скорости сторон
    left_speed = 0
    right_speed = 0

    # -------- ВПЕРЁД --------
    if "w" in pressed:
        left_speed += 60
        right_speed += 60

    # -------- НАЗАД --------
    if "s" in pressed:
        left_speed -= 60
        right_speed -= 60

    # -------- ВЛЕВО --------
    if "a" in pressed:
        left_speed -= 20   # замедляем левую сторону
        right_speed += 20  # ускоряем правую

    # -------- ВПРАВО --------
    if "d" in pressed:
        left_speed += 20
        right_speed -= 20

    # Ограничение скорости
    left_speed = max(-100, min(100, left_speed))
    right_speed = max(-100, min(100, right_speed))

    # --------------------------
    # Применяем скорость к моторам
    # --------------------------
    if left_speed >= 0:
        set_motor(pins["DIR1"], pwm1, 1, abs(left_speed))
        set_motor(pins["DIR3"], pwm3, 1, abs(left_speed))
    else:
        set_motor(pins["DIR1"], pwm1, 0, abs(left_speed))
        set_motor(pins["DIR3"], pwm3, 0, abs(left_speed))

    if right_speed >= 0:
        set_motor(pins["DIR2"], pwm2, 1, abs(right_speed))
        set_motor(pins["DIR4"], pwm4, 1, abs(right_speed))
    else:
        set_motor(pins["DIR2"], pwm2, 0, abs(right_speed))
        set_motor(pins["DIR4"], pwm4, 0, abs(right_speed))

def stop_all():
    for p in (pwm1, pwm2, pwm3, pwm4):
        p.ChangeDutyCycle(0)

# ================================
# Клавиатура
# ================================
def on_press(key):
    try:
        pressed.add(key.char)
    except:
        pass

def on_release(key):
    try:
        pressed.discard(key.char)
    except:
        pass

    if key == keyboard.Key.esc:
        return False

listener = keyboard.Listener(on_press=on_press, on_release=on_release)
listener.start()

# ================================
# Главный цикл
# ================================
try:
    print("Управление: W A S D | ESC — выход")
    while True:
        drive()
        time.sleep(0.03)

except KeyboardInterrupt:
    pass

finally:
    stop_all()
    GPIO.cleanup()
