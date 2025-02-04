from pymodbus.client import ModbusTcpClient
from pymodbus.client.mixin import ModbusClientMixin
from pymodbus.payload import BinaryPayloadDecoder
from models.base_models import DeviceConfig
from typing import List
from read_config import Logger


class ModbusModule(ModbusTcpClient):
    def __init__(self, host: str, port: int, modbus_device: DeviceConfig):
        super().__init__(host=host, port=port)
        self.modbus_device = modbus_device

    def read_decode_sequence_registers(
        self, initial_address: int, nr_measurements: int, data_type: ModbusClientMixin.DATATYPE
    ) -> list | None:

        data_type_length = data_type.value[1]
        read_result = self.read_holding_registers(
            address=initial_address, count=data_type_length * nr_measurements, slave=1
        )
        if read_result.isError():
            print(f"Errore nella lettua dei registri: {read_result}")
            return None
        registers = read_result.registers

        measurements = [registers[i : i + data_type_length] for i in range(0, len(registers), data_type_length)]
        list_data = []
        for measurement in measurements:
            data = self.convert_from_registers(registers=measurement, data_type=data_type)
            list_data.append(data)

        return list_data

    def read_device_config_measurements(self) -> List[dict]:
        register_readings = []
        collected_data = []
        for register in self.modbus_device.MEASUREMENTS:
            address_to_read = register.REGISTER_NUMBER
            data_type: ModbusClientMixin.DATATYPE = register.VALUE_TYPE
            data_type_length = data_type.value[1]
            read_result = self.read_holding_registers(address=address_to_read, count=data_type_length, slave=1)
            if read_result.isError():
                Logger.error(f"Errore nella lettura dei registri: {read_result}")
                continue
            decoder = BinaryPayloadDecoder.fromRegisters(
                registers=read_result.registers,
                byteorder=self.modbus_device.ENDIAN_BYTEORDER,
                wordorder=self.modbus_device.ENDIAN_WORDORDER,
            )
            if data_type is ModbusClientMixin.DATATYPE.FLOAT32:
                data = decoder.decode_32bit_float()
            elif data_type is ModbusClientMixin.DATATYPE.FLOAT64:
                data = decoder.decode_64bit_float()
            elif data_type is ModbusClientMixin.DATATYPE.INT16:
                data = decoder.decode_16bit_int()
            elif data_type is ModbusClientMixin.DATATYPE.INT32:
                data = decoder.decode_32bit_int()
            elif data_type is ModbusClientMixin.DATATYPE.INT64:
                data = decoder.decode_64bit_int()
            elif data_type is ModbusClientMixin.DATATYPE.UINT16:
                data = decoder.decode_16bit_uint()
            elif data_type is ModbusClientMixin.DATATYPE.UINT32:
                data = decoder.decode_32bit_uint()
            elif data_type is ModbusClientMixin.DATATYPE.UINT64:
                data = decoder.decode_64bit_uint()
            else:
                Logger.error(
                    f"Datatype del registro {register.REGISTER_NAME} non presente nei possibili da decodificare. \
                        Registri letti: {read_result.registers}"
                )

            # data = self.convert_from_registers(registers=read_result.registers, data_type=data_type)

            collected_data.append({"name": register.REGISTER_NAME, "value": data, "unit": register.UOM})
        return collected_data

    @staticmethod
    def convert_unit_of_measure(collected_data: List[dict]):
        for dict_data in collected_data:
            unit_of_measure: str = dict_data["unit"]
            if unit_of_measure.startswith("m"):
                dict_data["unit"] = unit_of_measure[1:]
                dict_data["value"] /= 1000
        return collected_data
