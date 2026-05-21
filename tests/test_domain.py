from src.Domain.house import Alarm, Door, HVAC, Light, ProximitySensor


class TestLight:
    def test_display_name_includes_index(self) -> None:
        light = Light(index=3, is_on=False)
        assert light.display_name == "Light 3"

    def test_status_text_when_on(self) -> None:
        light = Light(index=0, is_on=True)
        assert light.status_text == "ON"

    def test_status_text_when_off(self) -> None:
        light = Light(index=0, is_on=False)
        assert light.status_text == "OFF"


class TestDoor:
    def test_display_name_includes_index(self) -> None:
        door = Door(index=2, is_locked=True)
        assert door.display_name == "Door 2"

    def test_status_text_when_locked(self) -> None:
        door = Door(index=0, is_locked=True)
        assert door.status_text == "LOCKED"

    def test_status_text_when_unlocked(self) -> None:
        door = Door(index=0, is_locked=False)
        assert door.status_text == "UNLOCKED"


class TestProximitySensor:
    def test_display_name_includes_index(self) -> None:
        sensor = ProximitySensor(index=1, motion_detected=False)
        assert sensor.display_name == "Proximity Sensor 1"

    def test_status_text_when_motion_detected(self) -> None:
        sensor = ProximitySensor(index=0, motion_detected=True)
        assert sensor.status_text == "MOTION"

    def test_status_text_when_clear(self) -> None:
        sensor = ProximitySensor(index=0, motion_detected=False)
        assert sensor.status_text == "CLEAR"


class TestAlarm:
    def test_status_text_when_sounding(self) -> None:
        alarm = Alarm(enabled=True, sounding=True)
        assert alarm.status_text == "SOUNDING"

    def test_status_text_when_armed_and_silent(self) -> None:
        alarm = Alarm(enabled=True, sounding=False)
        assert alarm.status_text == "ARMED"

    def test_status_text_when_disarmed(self) -> None:
        alarm = Alarm(enabled=False, sounding=False)
        assert alarm.status_text == "DISARMED"

    def test_display_name(self) -> None:
        alarm = Alarm(enabled=False, sounding=False)
        assert alarm.display_name == "Alarm System"


class TestHVAC:
    def test_status_text_when_heating(self) -> None:
        hvac = HVAC(heater_on=True, chiller_on=False)
        assert hvac.status_text == "HEATING"

    def test_status_text_when_cooling(self) -> None:
        hvac = HVAC(heater_on=False, chiller_on=True)
        assert hvac.status_text == "COOLING"

    def test_status_text_when_idle(self) -> None:
        hvac = HVAC(heater_on=False, chiller_on=False)
        assert hvac.status_text == "IDLE"

    def test_display_name(self) -> None:
        hvac = HVAC(heater_on=False, chiller_on=False)
        assert hvac.display_name == "HVAC"