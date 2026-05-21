from src.Domain import House, InvalidHouseStateError


class HouseRegistry:
    def __init__(self) -> None:
        self._houses: dict[str, House] = {}

    def ensure_house(self, home_name: str) -> None:
        self._houses.setdefault(home_name, House(name=home_name))

    def describe_state(self, home_name: str) -> list[str]:
        return self._require_house(home_name).describe_lines()

    def to_state_map(self, home_name: str) -> dict[str, str]:
        return self._require_house(home_name).to_state_map()

    def apply_wire_update(self, home_name: str, updates: dict[str, str]) -> bool:
        house = self._require_house(home_name)
        try:
            house.apply_update_map(updates)
        except InvalidHouseStateError:
            return False
        return True

    def set_light(self, home_name: str, index: int, turn_on: bool) -> bool:
        house = self._require_house(home_name)
        house.set_light(index, turn_on)
        return True

    def set_door_lock(self, home_name: str, index: int, lock: bool) -> bool:
        house = self._require_house(home_name)
        house.set_door_lock(index, lock)
        return True

    def set_alarm(self, home_name: str, armed: bool) -> bool:
        house = self._require_house(home_name)
        house.set_alarm_enabled(armed)
        return True

    def set_hvac_mode(self, home_name: str, mode: str) -> bool:
        house = self._require_house(home_name)
        try:
            house.set_hvac_mode(mode)
        except InvalidHouseStateError:
            return False
        return True

    def _require_house(self, home_name: str) -> House:
        house = self._houses.get(home_name)
        if house is None:
            raise KeyError(f"No house state for '{home_name}'")
        return house
