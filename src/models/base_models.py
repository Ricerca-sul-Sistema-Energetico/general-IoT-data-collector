from pydantic import BaseModel
from pymodbus.client.mixin import ModbusClientMixin
from pymodbus.constants import Endian
from typing import List


class Register(BaseModel):
    REGISTER_NAME: str
    REGISTER_NUMBER: int
    VALUE_TYPE: ModbusClientMixin.DATATYPE
    UOM: str

    @classmethod
    def from_dict(cls, data):
        data["VALUE_TYPE"] = getattr(ModbusClientMixin.DATATYPE, data["VALUE_TYPE"])
        return cls(**data)


class DeviceConfig(BaseModel):
    ENDIAN_BYTEORDER: Endian
    ENDIAN_WORDORDER: Endian
    MEASUREMENTS: List[Register]

    @classmethod
    def from_json(cls, json_data):
        measurements = [Register.from_dict(measurement) for measurement in json_data["MEASUREMENTS"]]
        json_data["MEASUREMENTS"] = measurements
        return cls(**json_data)
