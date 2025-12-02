from flask import Flask, render_template_string, request
import RPi.GPIO as GPIO

# Налаштування GPIO
GPIO.setmode(GPIO.BCM)
pins = {
    "DIR1": 17, "PWM1": 18,   # Переднє ліве
    "DIR2": 22, "PWM2": 23,   # Переднє праве
    "DIR3": 24, "PWM3": 25,   # Заднє ліве
    "DIR4": 5,  "PWM4": 6     # Заднє праве
}
for pin in pins.values():
    GPIO.setup(pin, GPIO.OUT)

# PWM для кожного мотора
pwm1 = GPIO.PWM(pins["PWM1"], 100)
pwm2 = GPIO.PWM(pins["PWM2"], 100)
pwm3 = GPIO.PWM(pins["PWM3"], 100)
pwm4 = GPIO.PWM(pins["PWM4"], 100)
for pwm in [pwm1, pwm2, pwm3, pwm4]:
    pwm.start(0)

def set_motor(dir_pin, pwm_obj, direction, speed):
    GPIO.output(dir_pin, direction)
    pwm_obj.ChangeDutyCycle(speed)

def move(action):
    speed = 50  # 50% потужності
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

app = Flask(__name__)

html = """
<!DOCTYPE html>
<html>
<head>
<title>Robot Control</title>
<style>
button { width: 120px; height: 60px; font-size: 20px; margin: 10px; }
</style>
</head>
<body>
<h1>Control Robot</h1>
<form method="POST">
<button name="action" value="forward">Forward</button><br>
<button name="action" value="left">Left</button>
<button name="action" value="stop">Stop</button>
<button name="action" value="right">Right</button><br>
<button name="action" value="backward">Backward</button>
</form>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        move(request.form["action"])
    return render_template_string(html)

if __name__ == "__main__":
    try:
        app.run(host="0.0.0.0", port=5000)
    finally:
        pwm1.stop()
        pwm2.stop()
        pwm3.stop()
        pwm4.stop()
        GPIO.cleanup()