import pytest

from src.Domain import DeviceFactory, UnknownDeviceTypeError
from src.Domain.devices import Alarm, DoorLock, HVAC, Light, ProximitySensor, TemperatureSensor


def test_factory_creates_light() -> None:
    device = DeviceFactory.create_device(DeviceFactory.LIGHT, index=1, is_on=True)
    assert isinstance(device, Light)
    assert device.index == 1
    assert device.is_on is True


def test_factory_creates_door_lock() -> None:
    device = DeviceFactory.create_device(DeviceFactory.DOOR_LOCK, index=0, is_locked=False)
    assert isinstance(device, DoorLock)
    assert device.index == 0
    assert device.is_locked is False


def test_factory_creates_proximity_sensor() -> None:
    device = DeviceFactory.create_device(
        DeviceFactory.PROXIMITY_SENSOR, index=2, motion_detected=True
    )
    assert isinstance(device, ProximitySensor)
    assert device.index == 2
    assert device.motion_detected is True


def test_factory_creates_temperature_sensor() -> None:
    device = DeviceFactory.create_device(
        DeviceFactory.TEMPERATURE_SENSOR, index=0, temperature=24
    )
    assert isinstance(device, TemperatureSensor)
    assert device.temperature == 24


def test_factory_creates_alarm() -> None:
    device = DeviceFactory.create_device(
        DeviceFactory.ALARM, index=0, enabled=True, sounding=False
    )
    assert isinstance(device, Alarm)
    assert device.enabled is True
    assert device.sounding is False


def test_factory_creates_hvac() -> None:
    device = DeviceFactory.create_device(
        DeviceFactory.HVAC, index=0, heater_on=False, chiller_on=True
    )
    assert isinstance(device, HVAC)
    assert device.chiller_on is True


def test_factory_rejects_unknown_device_type() -> None:
    with pytest.raises(UnknownDeviceTypeError):
        DeviceFactory.create_device("unknown", index=0)
