import lgpio


GPIO_CHIP = 0
LED_PIN = 18


class LedController:
    """Control one LED connected to a Raspberry Pi GPIO pin."""

    def __init__(self, chip=GPIO_CHIP, pin=LED_PIN):
        self.pin = pin
        self._handle = lgpio.gpiochip_open(chip)
        lgpio.gpio_claim_output(self._handle, self.pin, 0)
        self._is_on = False

    @property
    def is_on(self):
        return self._is_on

    def turn_on(self):
        lgpio.gpio_write(self._handle, self.pin, 1)
        self._is_on = True

    def turn_off(self):
        lgpio.gpio_write(self._handle, self.pin, 0)
        self._is_on = False

    def toggle(self):
        if self._is_on:
            self.turn_off()
        else:
            self.turn_on()

    def close(self):
        if self._handle is not None:
            self.turn_off()
            lgpio.gpio_free(self._handle, self.pin)
            lgpio.gpiochip_close(self._handle)
            self._handle = None