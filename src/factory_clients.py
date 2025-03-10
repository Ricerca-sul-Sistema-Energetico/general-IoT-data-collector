import json
from typing import Dict
from paho.mqtt.client import Client as MqttClient, CallbackAPIVersion  # type: ignore
from read_config import (
    mqtt_config,
    influx_config,
    Logger,
    modbus_device_names,
    modbus_device_hosts,
    modbus_device_ports,
    project_name,
    field_name,
)

from models.base_models import DeviceConfig
from models.base_modbus import ModbusModule
from funcs.handlers import on_disconnect_mqtt, on_connect_mqtt, on_publish_mqtt
from influxdb import InfluxDBClient


modbus_module_dict: Dict[str, ModbusModule] = {}
for item in range(0, len(modbus_device_names)):
    try:
        device_name = modbus_device_names[item]
        host = modbus_device_hosts[item]
        port = int(modbus_device_ports[item])
        with open(f"config/{device_name.lower()}.json", "r") as file:
            mb_device_config_dict = json.load(file)
            mb_device_config = DeviceConfig.from_json(mb_device_config_dict)
            modbus_module = ModbusModule(host=host, port=port, modbus_device=mb_device_config)
            modbus_module_dict[device_name] = modbus_module
            connection = modbus_module.connect()
            if connection:
                Logger.info(f"Successful modbus initial connection with server {device_name}")
            else:
                Logger.warning(f"Failed modbus initial connection with server {device_name}")
    except Exception as e:
        Logger.error(f"Could not load modbus configuration for device {device_name}. Exception occoured: {e}")

try:
    if any(value is None for value in mqtt_config):
        mqtt_client = None
        Logger.info("MQTT client is None for this project")
    else:
        mqtt_client = MqttClient(
            callback_api_version=CallbackAPIVersion.VERSION2,
            client_id=f"{project_name}_{field_name}",
            clean_session=True,
        )
        mqtt_client.username_pw_set(username=mqtt_config.USER, password=mqtt_config.PASSWORD)
        mqtt_client.connect(
            host=mqtt_config.HOST,
            port=mqtt_config.PORT,
            keepalive=mqtt_config.KEEPALIVE,
        )
        mqtt_client.on_connect = on_connect_mqtt
        mqtt_client.on_disconnect = on_disconnect_mqtt
        mqtt_client.on_publish = on_publish_mqtt

except Exception as e:
    Logger.error(f"Could not connect MQTT client. Info: {e}")
    Logger.info("Influx client is None for this project")


try:
    if any(value is None for value in influx_config):
        influx_client = None
        Logger.info("Influx client is None for this project")

    else:
        Logger.info("Ready to istantiate influx client")
        influx_client = InfluxDBClient(
            host=influx_config.HOST,
            port=influx_config.PORT,
            username=influx_config.USER,
            password=influx_config.PASSWORD,
        )
        # verifica esistenza db
        lst = influx_client.get_list_database()
        check = next((item for item in lst if item["name"] == influx_config.DATABASE), None)
        if len(lst) == 0 or check is None:
            influx_client.create_database(influx_config.DATABASE)
        influx_client.switch_database(influx_config.DATABASE)
        Logger.info(f"Influx client created, database selected: {influx_client._database}")
except Exception as e:
    Logger.error(f"Could not connect influxdb client. Info: {e}")
