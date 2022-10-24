import ulogging
from lamp import Lamp
from slutils import NamedEnum, read_state

log = ulogging.getLogger(__name__)
log.setLevel(ulogging.DEBUG)


class RingLampMode:  # pylint: disable=too-few-public-methods
    WHITE = NamedEnum("WHITE", 1)
    YELLOW = NamedEnum("YELLOW", 2)
    BOTH = NamedEnum("BOTH", 3)
    VALUES = [WHITE, YELLOW, BOTH]

    @staticmethod
    def fromValue(value):
        for aEnum in RingLampMode.VALUES:
            if aEnum.value is value:
                log.info("Found enum %s", aEnum.name)
                return aEnum
        return None

    @staticmethod
    def fromName(name):
        for aEnum in RingLampMode.VALUES:
            if aEnum.name.lower() == name.lower():
                log.info("Found enum %s", aEnum.name)
                return aEnum
        return RingLampMode.BOTH


class RingLamp:
    def __init__(self, whitePin, yellowPin, freq):
        self.whiteLeds = Lamp(whitePin, freq)
        self.yellowlLeds = Lamp(yellowPin, freq)
        self.lamps = [self.yellowlLeds, self.whiteLeds]
        self._mode = RingLampMode.BOTH
        self._brightness = 120
        self.handleState(read_state())

    def _get_active_lamps(self):
        lamps = []
        if self._mode is RingLampMode.WHITE:
            lamps = [self.whiteLeds]
        elif self._mode is RingLampMode.YELLOW:
            lamps = [self.yellowlLeds]
        else:
            lamps = self.lamps
        log.info("Active lamps for enum %s are %s", self.mode.name, lamps)
        return lamps

    @property
    def is_on(self):
        return any(lamp.is_on for lamp in self.lamps)

    def turn_on(self):
        self.turn_off()
        for lamp in self._get_active_lamps():
            lamp.brightness = self._brightness
            lamp.turn_on()

    def turn_off(self):
        for lamp in self.lamps:
            lamp.turn_off()

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

    def get_mode(self):
        return self._mode

    def set_mode(self, mode):
        self._mode = mode

    def data(self):
        modeName = self._mode.name
        return {
            "state": "ON" if self.is_on else "OFF",
            "brightness": self.brightness,
            "effect": ' '.join(word[0].upper() + word[1:].lower() for word in modeName.split())
        }

    mode = property(get_mode, set_mode)
    brightness = property(get_brightness, set_brightness)

    def handleState(self, state):
        log.info("Handling state: %s", state)
        if "brightness" in state:
            self.brightness = int(state["brightness"])
        if "effect" in state:
            self.mode = RingLampMode.fromName(state["effect"])
        if "state" in state:
            if state["state"] == "ON":
                self.turn_on()
            else:
                self.turn_off()
