from dataclasses import dataclass


@dataclass
class Device:
    index: int = 0


@dataclass
class Light(Device):
    is_on: bool = False

    def turn_on(self) -> None:
        self.is_on = True

    def turn_off(self) -> None:
        self.is_on = False

    @property
    def display_name(self) -> str:
        return f"Light {self.index}"

    @property
    def status_text(self) -> str:
        return "ON" if self.is_on else "OFF"


@dataclass
class DoorLock(Device):
    is_locked: bool = False

    def lock(self) -> None:
        self.is_locked = True

    def unlock(self) -> None:
        self.is_locked = False

    @property
    def display_name(self) -> str:
        return f"Door {self.index}"

    @property
    def status_text(self) -> str:
        return "LOCKED" if self.is_locked else "UNLOCKED"


@dataclass
class ProximitySensor(Device):
    motion_detected: bool = False

    @property
    def display_name(self) -> str:
        return f"Proximity Sensor {self.index}"

    @property
    def status_text(self) -> str:
        return "MOTION" if self.motion_detected else "CLEAR"


@dataclass
class TemperatureSensor(Device):
    temperature: int = 0


@dataclass
class Alarm(Device):
    enabled: bool = False
    sounding: bool = False

    def enable(self) -> None:
        self.enabled = True

    def disable(self) -> None:
        self.enabled = False

    @property
    def display_name(self) -> str:
        return "Alarm System"

    @property
    def status_text(self) -> str:
        if self.sounding:
            return "SOUNDING"
        return "ARMED" if self.enabled else "DISARMED"


@dataclass
class HVAC(Device):
    heater_on: bool = False
    chiller_on: bool = False

    def set_heating(self) -> None:
        self.heater_on = True
        self.chiller_on = False

    def set_cooling(self) -> None:
        self.heater_on = False
        self.chiller_on = True

    def set_idle(self) -> None:
        self.heater_on = False
        self.chiller_on = False

    def is_valid(self) -> bool:
        return not (self.heater_on and self.chiller_on)

    @property
    def display_name(self) -> str:
        return "HVAC"

    @property
    def status_text(self) -> str:
        if self.heater_on:
            return "HEATING"
        if self.chiller_on:
            return "COOLING"
        return "IDLE"
