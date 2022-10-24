import json
import ulogging

log = ulogging.getLogger("utils")
log.setLevel(ulogging.DEBUG)


def remap(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min


max_brightness_scale = 255
# max_duty_scale = 1023
max_duty_scale = 700


def to_brightness(duty):
    return int(remap(duty, 0, max_duty_scale, 0, max_brightness_scale))


def to_duty(brightnessNr):
    return int(remap(brightnessNr, 0, max_brightness_scale, 0, max_duty_scale))


def _write_json_file(file_name, data):
    f = open(file_name, 'w')
    f.write(json.dumps(data))
    f.close()
    log.debug("Wrote to file: %s data: %s", file_name, data)


def _read_json_file(file_name):
    f = open(file_name, 'r')
    data = json.loads(f.read())
    f.close()
    log.debug("Read from file: %s data: %s", file_name, data)
    return data


def write_secrets(data):
    _write_json_file("secrets.json", data)


def read_secrets():
    return _read_json_file("secrets.json")


def write_state(data):
    _write_json_file("state.json", data)


def read_state():
    return _read_json_file("state.json")


class NamedEnum:  # pylint: disable=too-few-public-methods
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __eq__(self, other):
        if isinstance(other, NamedEnum):
            return self.value == other.value
        return False
