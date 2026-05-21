from typing import Any

from src.Domain.devices import Alarm, Device, DoorLock, HVAC, Light, ProximitySensor, TemperatureSensor


class UnknownDeviceTypeError(ValueError):
    pass


class DeviceFactory:
    """Simple Factory: the only place where concrete device types are selected."""

    LIGHT = "light"
    DOOR_LOCK = "door_lock"
    PROXIMITY_SENSOR = "proximity_sensor"
    TEMPERATURE_SENSOR = "temperature_sensor"
    ALARM = "alarm"
    HVAC = "hvac"

    @staticmethod
    def create_device(device_type: str, **kwargs: Any) -> Device:
        if device_type == DeviceFactory.LIGHT:
            return Light(index=int(kwargs["index"]), is_on=bool(kwargs["is_on"]))

        if device_type == DeviceFactory.DOOR_LOCK:
            return DoorLock(index=int(kwargs["index"]), is_locked=bool(kwargs["is_locked"]))

        if device_type == DeviceFactory.PROXIMITY_SENSOR:
            return ProximitySensor(
                index=int(kwargs["index"]), motion_detected=bool(kwargs["motion_detected"])
            )

        if device_type == DeviceFactory.TEMPERATURE_SENSOR:
            return TemperatureSensor(index=int(kwargs["index"]), temperature=int(kwargs["temperature"]))

        if device_type == DeviceFactory.ALARM:
            return Alarm(
                index=int(kwargs["index"]),
                enabled=bool(kwargs["enabled"]),
                sounding=bool(kwargs["sounding"]),
            )

        if device_type == DeviceFactory.HVAC:
            return HVAC(
                index=int(kwargs["index"]),
                heater_on=bool(kwargs["heater_on"]),
                chiller_on=bool(kwargs["chiller_on"]),
            )

        raise UnknownDeviceTypeError(f"Unknown device type: {device_type}")
