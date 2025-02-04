from enum import Enum, auto


class InputType(Enum):
    real = auto()
    simulation = auto()


class InfluxDBModule:

    def __init__(self, logger, config_dict: dict):
        self.logger = logger
        database = config_dict.get("DATABASE", None)
        host = config_dict.get("HOST", None)
        port = config_dict.get("PORT", None)
        username = config_dict.get("USERNAME", None)
        password = config_dict.get("PASSWORD", None)
        ssl = str(config_dict.get("SSL")).lower() == "true"
        verify_ssl = str(config_dict.get("VERIFY_SSL")).lower() == "true"

        if username is None:
            self.client = InfluxDBClient(host=host, port=port)
        elif ssl == False:
            self.client = InfluxDBClient(host=host, port=port, username=username, password=password)
        else:
            self.client = InfluxDBClient(
                host=host, port=port, username=username, password=password, ssl=ssl, verify_ssl=verify_ssl
            )
        # verifica esistenza db
        lst = self.client.get_list_database()
        check = next((item for item in lst if item["name"] == database), None)
        # ritorna l'indice:
        # index = next((i for i, item in enumerate(lst) if item["name"] == database), None)

        if len(lst) == 0 or check is None:
            self.client.create_database(database)
        self.client.switch_database(database)

    def disconnect(self):
        return self.client.close()
