from factory_clients import Logger, modbus_module_dict, mqtt_client, influx_client
from read_config import polling_interval, project_name, field_name
import time
from datetime import datetime as dt
import pytz
import json
import time

if mqtt_client is not None:
    mqtt_client.loop_start()  # Attiva threading asincrono per gestione connessione con broker mqtt

if __name__ == "__main__":
    Logger.info(f" Start reading modbus data with polling interval {polling_interval}")
    while True:
        time.sleep(polling_interval)  # type: ignore
        overall_modbus_measurements = {}
        for modbus_device, modbus_module in modbus_module_dict.items():
            if not modbus_module.connected:
                Logger.warning(f" Modbus server {modbus_device} not connected. Reconnecting ... ")
                connection = modbus_module.connect()
                Logger.info(f"Modbus server {modbus_device} reconnection attempt: {connection}")

            acquired_data = modbus_module.read_device_config_measurements()
            corrected_data = modbus_module.convert_unit_of_measure(acquired_data)
            overall_modbus_measurements[modbus_device] = corrected_data

        if len(overall_modbus_measurements) > 0:
            Logger.debug(f"Finished taking modbus measurements:{overall_modbus_measurements}")
            publish_time = dt.now(tz=pytz.utc).replace(microsecond=0)
            if mqtt_client is not None:
                if mqtt_client.is_connected():
                    Logger.debug("Beginning sending MQTT")
                    for device_name, data_list in overall_modbus_measurements.items():
                        for measurement in data_list:
                            measurement_name = measurement["name"]
                            payload = json.dumps({"value": measurement["value"], "timestamp": time.time()})
                            post = mqtt_client.publish(
                                topic=f"{project_name.lower()}/{field_name.lower()}/out/{device_name}/{measurement_name}",
                                payload=payload,
                            )

                            Logger.info(f"MQTT message published {device_name}/{measurement_name}")
                else:
                    Logger.info("MQTT client not connected. Waiting for automatic reconnection ...")

            if influx_client is not None:
                json_body = []
                for device_name, data_list in overall_modbus_measurements.items():
                    fields_dict = {}
                    for data in data_list:
                        fields_dict[data["name"]] = data["value"]
                    device_influx_dict = {
                        "measurement": device_name,
                        "time": f"{publish_time}",
                        "fields": fields_dict,
                        "tags": {"field": f"{field_name}", "average": "false"},
                    }
                    json_body.append(device_influx_dict)
                wrtite_result = influx_client.write_points(json_body)
                Logger.info(f"Finished wrtiting influx points with result: {wrtite_result} on field {field_name}")
        else:
            Logger.info("No modbus messages collected. Check modbus servers.")
