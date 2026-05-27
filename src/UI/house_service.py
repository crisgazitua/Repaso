from typing import cast

from src.Domain.device_factory import DeviceFactory
from src.Domain.house import Alarm, Door, House, HVAC, Light, ProximitySensor
from src.Server.tcp_server import CleverHomeTCPServer

class HouseService:
    def __init__(self, server: CleverHomeTCPServer) -> None:
        self._server = server

    def list_connected_homes(self) -> list[str]:
        return self._server.list_connected_hubs()

    def get_house(self, home_name: str) -> House | None:
        hub = self._server.get_hub(home_name)
        if hub is None:
            return None
        try:
            state = hub.send_get_state()
        except Exception:
            return None
        return self._dict_to_house(home_name, state)

    def toggle_light(self, home_name: str, index: int, current_on: bool) -> bool:
        hub = self._server.get_hub(home_name)
        if hub is None:
            return False
        new_value = "0" if current_on else "1"
        return hub.send_set_state({f"LS{index}": new_value})

    def toggle_door(self, home_name: str, index: int, current_locked: bool) -> bool:
        hub = self._server.get_hub(home_name)
        if hub is None:
            return False
        new_value = "0" if current_locked else "1"
        return hub.send_set_state({f"DS{index}": new_value})

    def toggle_alarm(self, home_name: str, current_enabled: bool) -> bool:
        hub = self._server.get_hub(home_name)
        if hub is None:
            return False
        new_value = "0" if current_enabled else "1"
        return hub.send_set_state({"AS": new_value})

    def cycle_hvac(self, home_name: str, current: HVAC) -> bool:
        hub = self._server.get_hub(home_name)
        if hub is None:
            return False
        if not current.heater_on and not current.chiller_on:
            updates = {"HS": "1", "CS": "0"}
        elif current.heater_on:
            updates = {"HS": "0", "CS": "1"}
        else:
            updates = {"HS": "0", "CS": "0"}
        return hub.send_set_state(updates)

    def _dict_to_house(self, name: str, state: dict[str, str]) -> House:
        temperature = int(state.get("TR", "20"))

        door_indices = sorted(
            int(k[2:]) for k in state if k.startswith("DS") and k[2:].isdigit()
        )
        light_indices = sorted(
            int(k[2:]) for k in state if k.startswith("LS") and k[2:].isdigit()
        )
        sensor_indices = sorted(
            int(k[2:]) for k in state if k.startswith("PS") and k[2:].isdigit()
        )

        return House(
            name=name,
            temperature=temperature,
            doors=[
                cast(
                    Door,
                    DeviceFactory.create_device(
                        DeviceFactory.DOOR_LOCK,
                        index=i,
                        is_locked=state[f"DS{i}"] == "1",
                    ),
                )
                for i in door_indices
            ],
            lights=[
                cast(
                    Light,
                    DeviceFactory.create_device(
                        DeviceFactory.LIGHT,
                        index=i,
                        is_on=state[f"LS{i}"] == "1",
                    ),
                )
                for i in light_indices
            ],
            proximity_sensors=[
                cast(
                    ProximitySensor,
                    DeviceFactory.create_device(
                        DeviceFactory.PROXIMITY_SENSOR,
                        index=i,
                        motion_detected=state[f"PS{i}"] == "1",
                    ),
                )
                for i in sensor_indices
            ],
            alarm=cast(
                Alarm,
                DeviceFactory.create_device(
                    DeviceFactory.ALARM,
                    index=0,
                    enabled=state.get("AS", "0") == "1",
                    sounding=state.get("AO", "0") == "1",
                ),
            ),
            hvac=cast(
                HVAC,
                DeviceFactory.create_device(
                    DeviceFactory.HVAC,
                    index=0,
                    heater_on=state.get("HS", "0") == "1",
                    chiller_on=state.get("CS", "0") == "1",
                ),
            ),
        )