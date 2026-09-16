import lgpio


GPIO_CHIP = 0
LED_PIN = 18
LED_PINS = (14, 15, 18)


class LedController:
    """Control the LEDs connected to the Raspberry Pi GPIO pins."""

    def __init__(self, chip=GPIO_CHIP, pins=LED_PINS, pin=None):
        self.pins = (pin,) if pin is not None else tuple(pins)
        self.pin = self.pins[-1]
        self._handle = lgpio.gpiochip_open(chip)
        self._states = {pin_number: False for pin_number in self.pins}
        try:
            for pin_number in self.pins:
                lgpio.gpio_claim_output(self._handle, pin_number, 0)
        except Exception:
            self.close()
            raise

    @property
    def is_on(self):
        return self._states[self.pin]

    @property
    def states(self):
        return dict(self._states)

    def turn_on(self):
        self.set_on(self.pin)

    def turn_off(self):
        self.set_off(self.pin)

    def set_on(self, pin):
        self._write(pin, True)

    def set_off(self, pin):
        self._write(pin, False)

    def set_all_off(self):
        for pin in self.pins:
            self.set_off(pin)

    def set_weather(self, weather):
        weather_to_pin = {"NANG": 14, "CO MAY": 15, "MUA": 18}
        selected_pin = weather_to_pin.get(weather)
        for pin in self.pins:
            self._write(pin, pin == selected_pin)

    def _write(self, pin, is_on):
        if pin not in self._states:
            raise ValueError(f"Unknown LED pin: {pin}")
        lgpio.gpio_write(self._handle, pin, int(is_on))
        self._states[pin] = is_on

    def toggle(self):
        if self.is_on:
            self.turn_off()
        else:
            self.turn_on()

    def close(self):
        if self._handle is not None:
            self.set_all_off()
            for pin in self.pins:
                lgpio.gpio_free(self._handle, pin)
            lgpio.gpiochip_close(self._handle)
            self._handle = None