import os
import logging
from collections import namedtuple
from dotenv import dotenv_values
from typing import List

MqttConfig = namedtuple("MqttConfig", "USER, PASSWORD, HOST, PORT, KEEPALIVE")
InfluxConfig = namedtuple("InfluxConfig", "USER, PASSWORD, HOST, PORT, DATABASE")
PostgreSQLConfig = namedtuple("PostgreSQL", "USER, PASSWORD, HOST, PORT, DATABASE, TABLE_NAME, COLUMN_NAMEA, COLUMN_NAMEB")

env_values = dotenv_values()


logging.basicConfig(level=os.environ.get("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)
logger.info(f" Setting logger with LOG_LEVEL: {os.environ.get('LOG_LEVEL', 'INFO')}")
project_name: str = env_values.get("PROJECT_NAME", None)  # type: ignore
field_name: str = env_values.get("FIELD_NAME", None)  # type: ignore

modbus_device_names = [value for key, value in env_values.items() if key.startswith("MB_DEVICE_NAME")]  # type: ignore
modbus_device_hosts = [value for key, value in env_values.items() if key.startswith("MB_DEVICE_HOST")]  # type: ignore
modbus_device_ports = [value for key, value in env_values.items() if key.startswith("MB_DEVICE_PORT")]  # type: ignore
polling_interval = float(env_values.get("POLLING_INTERVAL", 10.0))  # type: ignore


mqtt_config = MqttConfig(
    HOST=env_values.get("MQTT_HOST", None),
    PORT=int(env_values.get("MQTT_PORT", 1883)),  # type: ignore
    USER=env_values.get("MQTT_USER", None),
    PASSWORD=env_values.get("MQTT_PWD", None),
    KEEPALIVE=int(env_values.get("MQTT_KEEPALIVE", 60)),  # type: ignore
)

influx_config = InfluxConfig(
    HOST=env_values.get("INFLUX_HOST", None),
    PORT=int(env_values.get("INFLUX_PORT", 8086)),  # type: ignore
    DATABASE=(env_values.get("INFLUX_DATABASE", None)),  # type: ignore
    USER=env_values.get("INFLUX_USER", None),
    PASSWORD=env_values.get("INFLUX_PWD", None),
)

postgre_config = PostgreSQLConfig(
    HOST=env_values.get("POSTGRE_HOST", None),
    PORT=int(env_values.get("POSTGRE_PORT", 5432)),  # type: ignore
    DATABASE=(env_values.get("POSTGRE_DATABASE", "postgres")),
    USER=env_values.get("POSTGRE_USER", None),
    PASSWORD=env_values.get("POSTGRE_PWD", None),
    TABLE_NAME=env_values.get("POSTGRE_TABLE_NAME", None),
    COLUMN_NAMEA=env_values.get("POSTGRE_COLUMN_NAMEA", "timestamp"),
    COLUMN_NAMEB=env_values.get("POSTGRE_COLUMN_NAMEB", '"production_W"')
)

logging.basicConfig(level=os.environ.get("LOG_LEVEL", "INFO"))
Logger = logging.getLogger(__name__)
Logger.info(" Launching modbus application ...")
