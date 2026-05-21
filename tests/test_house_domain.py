import pytest

from src.Domain import House, InvalidHouseStateError


def test_house_updates_dynamically_from_state_map() -> None:
    house = House(name="home-a")

    house.update_from_state_map(
        {
            "TR": "25",
            "DS0": "1",
            "DS2": "0",
            "LS0": "1",
            "LS4": "0",
            "PS0": "1",
            "AS": "1",
            "AO": "1",
            "HS": "0",
            "CS": "1",
        }
    )

    assert house.temperature == 25
    assert house.doors[0].is_locked is True
    assert house.doors[2].is_locked is False
    assert house.lights[0].is_on is True
    assert house.lights[4].is_on is False
    assert house.proximity_sensors[0].motion_detected is True
    assert house.alarm.enabled is True
    assert house.alarm.sounding is True
    assert house.hvac.chiller_on is True


def test_house_rejects_invalid_hvac_combination() -> None:
    house = House(name="home-a")

    with pytest.raises(InvalidHouseStateError):
        house.apply_update_map({"HS": "1", "CS": "1"})


def test_house_rejects_forced_alarm_output_zero() -> None:
    house = House(name="home-a")

    with pytest.raises(InvalidHouseStateError):
        house.apply_update_map({"AO": "0"})
