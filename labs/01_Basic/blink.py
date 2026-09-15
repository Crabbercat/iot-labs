import lgpio
import time

GPIO_PIN = 18

h = lgpio.gpiochip_open(0)

try:
    lgpio.gpio_claim_output(h, GPIO_PIN, 0)

    while True:
        lgpio.gpio_write(h, GPIO_PIN, 1)
        print("LED ON")
        time.sleep(1)

        lgpio.gpio_write(h, GPIO_PIN, 0)
        print("LED OFF")
        time.sleep(1)

except KeyboardInterrupt:
    print("\nStopping...")

finally:
    lgpio.gpio_free(h, GPIO_PIN)
    lgpio.gpiochip_close(h)
