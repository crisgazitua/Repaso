from dataclasses import dataclass, field

@dataclass
class Light:
    index: int
    is_on: bool

    @property
    def display_name(self) -> str:
        return f"Light {self.index}"

    @property
    def status_text(self) -> str:
        return "ON" if self.is_on else "OFF"


@dataclass
class Door:
    index: int
    is_locked: bool

    @property
    def display_name(self) -> str:
        return f"Door {self.index}"

    @property
    def status_text(self) -> str:
        return "LOCKED" if self.is_locked else "UNLOCKED"


@dataclass
class ProximitySensor:
    index: int
    motion_detected: bool

    @property
    def display_name(self) -> str:
        return f"Proximity Sensor {self.index}"

    @property
    def status_text(self) -> str:
        return "MOTION" if self.motion_detected else "CLEAR"


@dataclass
class Alarm:
    enabled: bool
    sounding: bool

    @property
    def display_name(self) -> str:
        return "Alarm System"

    @property
    def status_text(self) -> str:
        if self.sounding:
            return "SOUNDING"
        return "ARMED" if self.enabled else "DISARMED"


@dataclass
class HVAC:
    heater_on: bool
    chiller_on: bool

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


@dataclass
class House:
    name: str
    temperature: int
    lights: list[Light] = field(default_factory=list)
    doors: list[Door] = field(default_factory=list)
    proximity_sensors: list[ProximitySensor] = field(default_factory=list)
    alarm: Alarm = field(default_factory=lambda: Alarm(enabled=False, sounding=False))
    hvac: HVAC = field(default_factory=lambda: HVAC(heater_on=False, chiller_on=False))