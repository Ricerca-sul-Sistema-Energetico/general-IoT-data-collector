from paho.mqtt.client import Client as MqttClient
from read_config import Logger


def on_disconnect_mqtt(client: MqttClient, userdata, flags, rc, properties):
    Logger.error(f"MQTT client disconnected with result code {rc}")
    # client.reconnect()


def on_connect_mqtt(client, userdata, flags, reason_code, properties):
    Logger.info(f"MQTT client connected with result code {reason_code}")


def on_publish_mqtt(client: MqttClient, userdata, mid, reason_code, properties):
    Logger.debug(f"MQTT message sending result: client:{client} \n mids: {mid}; \n code: {reason_code}")
