import RPi.GPIO as GPIO
import time

SERVO_PIN = 18
BUTTON_PIN = 22

GPIO.setmode(GPIO.BCM)
GPIO.setup(SERVO_PIN, GPIO.OUT)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

pwm = GPIO.PWM(SERVO_PIN, 50)
pwm.start(0)


def set_angle(angle):
    duty = 2 + (angle / 18)

    print(f"[SERVO] Moving to {angle}° (duty={duty:.2f}%)")

    GPIO.output(SERVO_PIN, True)
    pwm.ChangeDutyCycle(duty)

    time.sleep(0.5)

    GPIO.output(SERVO_PIN, False)
    pwm.ChangeDutyCycle(0)

    print(f"[SERVO] Reached {angle}°")


state = 0

print("================================")
print(" Servo + Button Controller")
print("================================")
print(f"[INIT] Servo pin : GPIO {SERVO_PIN}")
print(f"[INIT] Button pin: GPIO {BUTTON_PIN}")
print("[INIT] Initial state: 0 (0°)")
print("[READY] Waiting for button...")
print("--------------------------------")


try:
    while True:
        if GPIO.input(BUTTON_PIN) == GPIO.LOW:

            print("[BUTTON] Button pressed")

            if state == 0:
                print("[STATE] 0 -> 1")
                set_angle(180)
                state = 1
                print("[STATE] Current state: 1")

            else:
                print("[STATE] 1 -> 0")
                set_angle(0)
                state = 0
                print("[STATE] Current state: 0")

            print("[BUTTON] Waiting for button release...")

            time.sleep(0.3)

            while GPIO.input(BUTTON_PIN) == GPIO.LOW:
                time.sleep(0.05)

            print("[BUTTON] Button released")
            print("--------------------------------")

        time.sleep(0.05)


except KeyboardInterrupt:
    print("\n[EXIT] Program interrupted by user")

finally:
    pwm.stop()
    GPIO.cleanup()
    print("[CLEANUP] GPIO cleaned up")
    print("[EXIT] Program stopped")