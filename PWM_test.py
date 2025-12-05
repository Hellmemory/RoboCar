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
    left_speed = 0
    right_speed = 0
    
    # 1. Определяем базовую скорость (Газ / Назад)
    base_speed = 0
    if "w" in pressed:
        base_speed = 60
    elif "s" in pressed:
        base_speed = -60

    # 2. Применяем повороты ТОЛЬКО если машина едет
    if base_speed != 0:
        left_speed = base_speed
        right_speed = base_speed
        
        turn_val = 30 # Насколько сильно менять скорость при повороте

        if "a" in pressed:
            # Поворот влево: левая сторона медленнее, правая быстрее
            left_speed -= turn_val
            right_speed += turn_val
        
        if "d" in pressed:
            # Поворот вправо: левая сторона быстрее, правая медленнее
            left_speed += turn_val
            right_speed -= turn_val

    # Если газ не нажат — скорости остаются 0 (машина не крутится на месте)

    # Ограничение скорости (-100 до 100)
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