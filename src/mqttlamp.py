import json
import ulogging
import ubinascii
import machine
# import umqtt.robust as mqtt
import umqtt.simple as mqtt
import uasyncio as asyncio
import slutils
import wifiutils
from ringlight import RingLamp

log = ulogging.getLogger(__name__)
log.setLevel(ulogging.DEBUG)


def main():
    secrets = slutils.read_secrets()
    lamp = RingLamp(whitePin=12, yellowPin=13, freq=5000)
    mqtt_client = mqtt.MQTTClient(MQTTLamp.CLIENT_ID,
                                  secrets["mqtt"]["host"],
                                  secrets["mqtt"]["port"],
                                  secrets["mqtt"]["user"],
                                  secrets["mqtt"]["password"],
                                  5)

    mqtt_lamp = MQTTLamp(mqtt_client, lamp)
    wifiutils.register_on_connect_callback(mqtt_lamp.connect)
    loop = asyncio.get_event_loop()
    mqtt_lamp.connect(True)
    loop.create_task(mqtt_lamp.await_message())
    loop.create_task(mqtt_lamp.ping())
    loop.run_forever()


class MQTTLamp:
    CLIENT_ID = ubinascii.hexlify(machine.unique_id()).decode('utf-8')
    log.info("ID %s", CLIENT_ID)
    DISCOVERY_TOPIC = f"homeassistant/light/{CLIENT_ID}/light/config"
    JSON_TOPIC = f"esp32/{CLIENT_ID}"
    SET_TOPIC = f"esp32/{CLIENT_ID}/set"
    AVAILIBILITY_TOPIC = f"esp32/{CLIENT_ID}/availibility"
    CLIENTS_TOPIC = "$SYS/broker/clients/connected"
    MQTT_DEVICE = {
        "identifiers": [f"esp32_{CLIENT_ID}"],
        "manufacturer": "blackstardlb",
        "model": "esp32 ring light",
        "name": "Ring Light"
    }
    MQTT_DISCOVERY_DATA = {
        "availability": [
            {
                "topic": AVAILIBILITY_TOPIC
            }
        ],
        "brightness": True,
        "brightness_scale": 255,
        "command_topic": SET_TOPIC,
        "device": MQTT_DEVICE,
        "effect": True,
        "effect_list": [
            "White",
            "Yellow",
            "Both"
        ],
        "json_attributes_topic":  JSON_TOPIC,
        "name": "Ring Light",
        "schema": "json",
        "state_topic": JSON_TOPIC,
        "unique_id": f"{CLIENT_ID}_light_esp32"
    }

    def __init__(self, client: mqtt.MQTTClient, lamp: RingLamp):
        self.client = client
        self.lamp = lamp

    def publish_state(self):
        state_json = json.dumps(self.lamp.data())
        self.publish(MQTTLamp.JSON_TOPIC, state_json)

    def publish_online(self):
        self.publish(MQTTLamp.AVAILIBILITY_TOPIC, "online", True)

    def publish_discovery_data(self):
        self.publish(
            MQTTLamp.DISCOVERY_TOPIC,
            json.dumps(MQTTLamp.MQTT_DISCOVERY_DATA),
            True
        )

    def handle_message(self, message):
        topic = message[0]
        msg = message[1]
        if (topic == MQTTLamp.AVAILIBILITY_TOPIC and msg != "online"):
            self.publish_online()
        if topic == MQTTLamp.SET_TOPIC:
            state = json.loads(msg)
            self.lamp.handleState(state)
            self.publish_state()
            slutils.write_state(self.lamp.data())
        if topic == MQTTLamp.CLIENTS_TOPIC:
            self.publish_state()

    def on_message(self, topic, msg):
        topic = topic.decode('UTF-8')
        msg = msg.decode('UTF-8')
        log.info("Topic: %s sent message: %s", topic, msg)
        self.handle_message((topic, msg))

    def connect(self, clear=False):
        try: 
            log.debug("Connecting")
            self.client.set_callback(self.on_message)
            self.client.set_last_will(MQTTLamp.AVAILIBILITY_TOPIC, "offline", True)
            self.client.connect(clear)
            self.client.subscribe(MQTTLamp.SET_TOPIC)
            self.client.subscribe(MQTTLamp.AVAILIBILITY_TOPIC)
            self.client.subscribe(MQTTLamp.CLIENTS_TOPIC)
            self.publish_discovery_data()
            self.publish_online()
            self.publish_state()
        except OSError: # type: ignore
            log.debug("Failed to connect retrying in 5s")

    async def ping(self):
        while True:
            if wifiutils.is_network_connected():
                try:
                    self.client.ping()
                except OSError: # type: ignore
                    log.warning("failed to ping message")
                    self.connect()
            await asyncio.sleep(2)

    async def await_message(self):
        while True:
            if wifiutils.is_network_connected():
                try:
                    self.client.check_msg()
                except OSError: # type: ignore
                    log.warning("failed to await message")
                    self.connect()
            await asyncio.sleep_ms(200)

    def publish(self, topic, data, persist=False):
        def sendMessage():
            try:
                log.debug("Publishing %s to %s", data, topic)
                self.client.publish(topic, data, persist)
            except OSError: # type: ignore
                log.warning("failed to publish message to topic %s", topic)
                self.connect()
        if wifiutils.is_network_connected():
            sendMessage()

    def doNothing(self):
        return 1+1
