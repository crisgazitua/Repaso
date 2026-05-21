from dataclasses import dataclass, field
from typing import cast

from src.Domain.device_factory import DeviceFactory
from src.Domain.devices import Alarm, DoorLock, HVAC, Light, ProximitySensor
from src.Protocol import (
    BINARY_ONE,
    BINARY_ZERO,
    KEY_AO,
    KEY_AS,
    KEY_CS,
    KEY_HS,
    KEY_TR,
    PREFIX_DS,
    PREFIX_LS,
    PREFIX_PS,
)


class InvalidHouseStateError(ValueError):
    pass


# Backward-compatible alias for modules/tests that still import Door from house.py.
Door = DoorLock

__all__ = [
    "House",
    "InvalidHouseStateError",
    "Door",
    "DoorLock",
    "Light",
    "ProximitySensor",
    "Alarm",
    "HVAC",
]


@dataclass
class House:
    name: str
    temperature: int = 0
    doors: dict[int, DoorLock] = field(default_factory=dict)
    lights: dict[int, Light] = field(default_factory=dict)
    proximity_sensors: dict[int, ProximitySensor] = field(default_factory=dict)
    alarm: Alarm = field(default_factory=lambda: Alarm(index=0, enabled=False, sounding=False))
    hvac: HVAC = field(default_factory=lambda: HVAC(index=0, heater_on=False, chiller_on=False))

    def set_light(self, index: int, is_on: bool) -> None:
        light = self.lights.get(index)
        if light is None:
            light = cast(
                Light,
                DeviceFactory.create_device(DeviceFactory.LIGHT, index=index, is_on=False),
            )
            self.lights[index] = light
        if is_on:
            light.turn_on()
        else:
            light.turn_off()

    def set_door_lock(self, index: int, is_locked: bool) -> None:
        door = self.doors.get(index)
        if door is None:
            door = cast(
                DoorLock,
                DeviceFactory.create_device(
                    DeviceFactory.DOOR_LOCK, index=index, is_locked=False
                ),
            )
            self.doors[index] = door
        if is_locked:
            door.lock()
        else:
            door.unlock()

    def set_alarm_enabled(self, enabled: bool) -> None:
        if enabled:
            self.alarm.enable()
        else:
            self.alarm.disable()

    def set_hvac_mode(self, mode: str) -> None:
        if mode == "heat":
            self.hvac.set_heating()
        elif mode == "cool":
            self.hvac.set_cooling()
        elif mode == "idle":
            self.hvac.set_idle()
        else:
            raise InvalidHouseStateError(f"Unknown HVAC mode: {mode}")

    def describe_lines(self) -> list[str]:
        lines = [f"Temperature: {self.temperature}"]

        lines.append("Doors:")
        for index in sorted(self.doors.keys()):
            status = "LOCKED" if self.doors[index].is_locked else "UNLOCKED"
            lines.append(f"  Door {index}: {status}")

        lines.append("Lights:")
        for index in sorted(self.lights.keys()):
            status = "ON" if self.lights[index].is_on else "OFF"
            lines.append(f"  Light {index}: {status}")

        lines.append("Proximity Sensors:")
        for index in sorted(self.proximity_sensors.keys()):
            status = "MOTION" if self.proximity_sensors[index].motion_detected else "CLEAR"
            lines.append(f"  Sensor {index}: {status}")

        lines.append(f"Alarm: {'ARMED' if self.alarm.enabled else 'DISARMED'}")
        if self.hvac.heater_on:
            lines.append("HVAC: HEATING")
        elif self.hvac.chiller_on:
            lines.append("HVAC: COOLING")
        else:
            lines.append("HVAC: IDLE")

        return lines

    def update_from_state_map(self, state: dict[str, str]) -> None:
        for key, value in state.items():
            if key == KEY_TR:
                self.temperature = int(value)
                continue

            if key.startswith(PREFIX_DS):
                self.set_door_lock(int(key[2:]), _binary_to_bool(value))
                continue

            if key.startswith(PREFIX_LS):
                self.set_light(int(key[2:]), _binary_to_bool(value))
                continue

            if key.startswith(PREFIX_PS):
                index = int(key[2:])
                sensor = DeviceFactory.create_device(
                    DeviceFactory.PROXIMITY_SENSOR,
                    index=index,
                    motion_detected=_binary_to_bool(value),
                )
                self.proximity_sensors[index] = cast(ProximitySensor, sensor)
                continue

            if key == KEY_AS:
                self.set_alarm_enabled(_binary_to_bool(value))
                continue

            if key == KEY_AO:
                self.alarm.sounding = _binary_to_bool(value)
                continue

            if key == KEY_HS:
                self.hvac.heater_on = _binary_to_bool(value)
                continue

            if key == KEY_CS:
                self.hvac.chiller_on = _binary_to_bool(value)
                continue

        if not self.hvac.is_valid():
            raise InvalidHouseStateError("Invalid HVAC state: heater and chiller cannot be ON at the same time")

    def apply_update_map(self, updates: dict[str, str]) -> None:
        if KEY_AO in updates and updates[KEY_AO] == BINARY_ZERO:
            raise InvalidHouseStateError("Alarm output cannot be forced to 0")

        merged = self.to_state_map()
        merged.update(updates)
        self.update_from_state_map(merged)

    def to_state_map(self) -> dict[str, str]:
        result: dict[str, str] = {KEY_TR: str(self.temperature)}

        for index in sorted(self.doors.keys()):
            result[f"{PREFIX_DS}{index}"] = _bool_to_binary(self.doors[index].is_locked)

        for index in sorted(self.lights.keys()):
            result[f"{PREFIX_LS}{index}"] = _bool_to_binary(self.lights[index].is_on)

        for index in sorted(self.proximity_sensors.keys()):
            result[f"{PREFIX_PS}{index}"] = _bool_to_binary(self.proximity_sensors[index].motion_detected)

        result[KEY_AS] = _bool_to_binary(self.alarm.enabled)
        result[KEY_AO] = _bool_to_binary(self.alarm.sounding)
        result[KEY_HS] = _bool_to_binary(self.hvac.heater_on)
        result[KEY_CS] = _bool_to_binary(self.hvac.chiller_on)
        return result


def _binary_to_bool(value: str) -> bool:
    return value == BINARY_ONE


def _bool_to_binary(value: bool) -> str:
    return BINARY_ONE if value else BINARY_ZERO
