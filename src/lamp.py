from machine import Pin, PWM
import ulogging
import slutils

log = ulogging.getLogger(__name__)
log.setLevel(ulogging.INFO)


class Lamp:
    def __init__(self, pin, freq):
        self._pin = pin
        self.led = PWM(Pin(pin), freq=freq, duty_ns=0)
        self._brightness = 0

    @property
    def is_on(self):
        return self.led.duty() > 0

    def turn_on(self):
        duty = slutils.to_duty(self._brightness)
        log.debug("Setting lamp Pin(%s) duty to %s", self._pin, duty)
        self.led.duty(duty)

    def turn_off(self):
        duty = 0
        log.debug("Setting lamp Pin(%s) duty to %s", self._pin, duty)
        self.led.duty(0)

    def toggle(self):
        if self.is_on:
            self.turn_off()
        else:
            self.turn_on()

    def set_brightness(self, brightness):
        if brightness == 0:
            self.turn_off()
            return
        self._brightness = brightness

    def get_brightness(self):
        return self._brightness

    def data(self):
        return {
            "status": "on" if self.is_on else "off",
            "brightness": self.brightness
        }

    brightness = property(get_brightness, set_brightness)

    def __str__(self):
        return f"led={self.led}, brightness={self.brightness}"
