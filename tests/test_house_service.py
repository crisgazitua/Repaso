import pytest
from src.Credentials.credential import Credential
from src.Credentials.in_memory_credential_store import InMemoryCredentialStore
from src.Domain.house import Alarm, Door, House, HVAC, Light, ProximitySensor
from src.Server.tcp_server import CleverHomeTCPServer
from src.UI.house_service import HouseService


@pytest.fixture
def service() -> HouseService:
    store = InMemoryCredentialStore(
        initial_credentials=[
            Credential(username="hub1", password="pass", home_name="home-a")
        ]
    )
    server = CleverHomeTCPServer(host="127.0.0.1", port=19999, credential_store=store)
    return HouseService(server)


@pytest.fixture
def full_state() -> dict[str, str]:
    return {
        "TR": "21",
        "DS0": "1", "DS1": "0", "DS2": "1",
        "LS0": "1", "LS1": "0", "LS2": "1", "LS3": "0", "LS4": "0",
        "PS0": "0", "PS1": "1",
        "AS": "1", "AO": "0",
        "HS": "1", "CS": "0",
    }


class TestDictToHouseDeviceDiscovery:
    def test_discovers_all_doors_from_state(
        self, service: HouseService, full_state: dict[str, str]
    ) -> None:
        house = service._dict_to_house("home-a", full_state)
        assert len(house.doors) == 3

    def test_discovers_all_lights_from_state(
        self, service: HouseService, full_state: dict[str, str]
    ) -> None:
        house = service._dict_to_house("home-a", full_state)
        assert len(house.lights) == 5

    def test_discovers_all_proximity_sensors_from_state(
        self, service: HouseService, full_state: dict[str, str]
    ) -> None:
        house = service._dict_to_house("home-a", full_state)
        assert len(house.proximity_sensors) == 2

    def test_house_with_no_doors_or_lights_is_valid(
        self, service: HouseService
    ) -> None:
        minimal_state = {
            "TR": "20", "AS": "0", "AO": "0", "HS": "0", "CS": "0"
        }
        house = service._dict_to_house("home-b", minimal_state)
        assert len(house.doors) == 0
        assert len(house.lights) == 0
        assert len(house.proximity_sensors) == 0

    def test_devices_are_sorted_by_index(
        self, service: HouseService
    ) -> None:
        state = {"TR": "20", "DS2": "1", "DS0": "0", "DS1": "1",
                 "AS": "0", "AO": "0", "HS": "0", "CS": "0"}
        
        house = service._dict_to_house("home-a", state)
        assert [d.index for d in house.doors] == [0, 1, 2]


class TestDictToHouseDeviceStates:
    def test_locked_door_parses_correctly(
        self, service: HouseService, full_state: dict[str, str]
    ) -> None:
        house = service._dict_to_house("home-a", full_state)
        
        assert house.doors[0].is_locked is True

    def test_unlocked_door_parses_correctly(
        self, service: HouseService, full_state: dict[str, str]
    ) -> None:
        
        house = service._dict_to_house("home-a", full_state)
        
        assert house.doors[1].is_locked is False

    def test_light_on_parses_correctly(
        self, service: HouseService, full_state: dict[str, str]
    ) -> None:
        
        house = service._dict_to_house("home-a", full_state)
        
        assert house.lights[0].is_on is True

    def test_light_off_parses_correctly(
        self, service: HouseService, full_state: dict[str, str]
    ) -> None:
        
        house = service._dict_to_house("home-a", full_state)
        
        assert house.lights[1].is_on is False

    def test_temperature_parses_correctly(
        self, service: HouseService, full_state: dict[str, str]
    ) -> None:
        
        house = service._dict_to_house("home-a", full_state)
        
        assert house.temperature == 21

    def test_missing_temperature_defaults_to_20(
        self, service: HouseService
    ) -> None:
        state = {"AS": "0", "AO": "0", "HS": "0", "CS": "0"}
        
        house = service._dict_to_house("home-a", state)
        
        assert house.temperature == 20

    def test_proximity_sensor_with_motion_parses_correctly(
        self, service: HouseService, full_state: dict[str, str]
    ) -> None:
        
        house = service._dict_to_house("home-a", full_state)
        
        assert house.proximity_sensors[1].motion_detected is True

    def test_proximity_sensor_clear_parses_correctly(
        self, service: HouseService, full_state: dict[str, str]
    ) -> None:
        
        house = service._dict_to_house("home-a", full_state)
        
        assert house.proximity_sensors[0].motion_detected is False


class TestDictToHouseHVAC:
    def test_heater_on_parses_correctly(
        self, service: HouseService, full_state: dict[str, str]
    ) -> None:
        house = service._dict_to_house("home-a", full_state)
        
        assert house.hvac.heater_on is True
        assert house.hvac.chiller_on is False

    def test_chiller_on_parses_correctly(self, service: HouseService) -> None:
        
        state = {"TR": "20", "AS": "0", "AO": "0", "HS": "0", "CS": "1"}
        
        house = service._dict_to_house("home-a", state)
        
        assert house.hvac.heater_on is False
        assert house.hvac.chiller_on is True

    def test_hvac_idle_parses_correctly(self, service: HouseService) -> None:
        
        state = {"TR": "20", "AS": "0", "AO": "0", "HS": "0", "CS": "0"}
        
        house = service._dict_to_house("home-a", state)
        
        assert house.hvac.heater_on is False
        assert house.hvac.chiller_on is False



class TestDictToHouseAlarm:
    def test_alarm_armed_parses_correctly(
        self, service: HouseService, full_state: dict[str, str]
    ) -> None:
        
        house = service._dict_to_house("home-a", full_state)
        
        assert house.alarm.enabled is True
        assert house.alarm.sounding is False

    def test_alarm_sounding_parses_correctly(self, service: HouseService) -> None:
        
        state = {"TR": "20", "AS": "1", "AO": "1", "HS": "0", "CS": "0"}
        
        house = service._dict_to_house("home-a", state)
        
        assert house.alarm.enabled is True
        assert house.alarm.sounding is True

    def test_alarm_disarmed_parses_correctly(self, service: HouseService) -> None:
        state = {"TR": "20", "AS": "0", "AO": "0", "HS": "0", "CS": "0"}
        house = service._dict_to_house("home-a", state)
        assert house.alarm.enabled is False
        assert house.alarm.sounding is False



class TestDictToHouseIdentity:
    def test_house_name_is_set_correctly(
        self, service: HouseService, full_state: dict[str, str]
    ) -> None:
        expected_name = "my-house"
        house = service._dict_to_house(expected_name, full_state)
        assert house.name == expected_name