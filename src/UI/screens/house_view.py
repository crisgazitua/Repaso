from typing import Any, Callable
from prompt_toolkit.formatted_text import FormattedText
from prompt_toolkit.key_binding import KeyBindings, KeyPressEvent
from prompt_toolkit.layout.containers import AnyContainer, HSplit, Window
from prompt_toolkit.layout.controls import FormattedTextControl
from src.Domain import house
from src.UI.screens.base import Screen


class HouseViewScreen(Screen):
    def __init__(self, controller, home_name: str) -> None:  # type: ignore[no-untyped-def]
        super().__init__(controller)
        self._home_name = home_name
        self._selected_index: int = 0

    def _rows(self) -> list[dict[str, Any]]:
        house = self._controller.service.get_house(self._home_name)
        if house is None:
            return []

        service = self._controller.service
        name = self._home_name
        rows: list[dict[str, Any]] = []

        rows.append({
            "section": "Climate",
            "label": "Temperature",
            "value": f"{house.temperature}°C",
            "readonly": True,
            "toggle": None,
        })
        rows.append({
            "section": "Climate",
            "label": house.hvac.display_name,
            "value": house.hvac.status_text,
            "readonly": False,
            "toggle": lambda h=house.hvac: service.cycle_hvac(name, h),
        })

        for light in house.lights:
            rows.append({
                "section": "Lights",
                "label": light.display_name,
                "value": light.status_text,
                "readonly": False,
                "toggle": lambda i=light.index, on=light.is_on: service.toggle_light(name, i, on),
            })

        for door in house.doors:
            rows.append({
                "section": "Doors",
                "label": door.display_name,
                "value": door.status_text,
                "readonly": False,
                "toggle": lambda i=door.index, locked=door.is_locked: service.toggle_door(name, i, locked),
            })

        for sensor in house.proximity_sensors:
            rows.append({
                "section": "Sensors",
                "label": sensor.display_name,
                "value": sensor.status_text,
                "readonly": True,
                "toggle": None,
            })

        rows.append({
            "section": "Security",
            "label": house.alarm.display_name,
            "value": house.alarm.status_text,
            "readonly": False,
            "toggle": lambda enabled=house.alarm.enabled: service.toggle_alarm(name, enabled),
        })

        return rows

    def _render(self) -> FormattedText:
        lines: list[tuple[str, str]] = []
        lines.append(("bold", f"  House: {self._home_name}\n"))
        lines.append(("", "  " + "─" * 50 + "\n"))

        rows = self._rows()

        if not rows:
            lines.append(("", f"\n  Hub '{self._home_name}' is not connected.\n"))
            lines.append(("", "  Press [b] to go back.\n"))
            return FormattedText(lines)

        if self._selected_index >= len(rows):
            self._selected_index = max(0, len(rows) - 1)

        current_section: str | None = None
        for i, row in enumerate(rows):
            if row["section"] != current_section:
                current_section = row["section"]
                lines.append(("bold", f"\n  {current_section}\n"))

            marker = "▶ " if i == self._selected_index else "  "
            style = "reverse" if i == self._selected_index else ""
            tag = "  (read-only)" if row["readonly"] else ""
            text = f"  {marker}{row['label']:<24}{row['value']:<12}{tag}\n"
            lines.append((style, text))

        return FormattedText(lines)

    def container(self) -> AnyContainer:  
        return HSplit([
            Window(content=FormattedTextControl(text=self._render), wrap_lines=False),
        ])

    def bottom_toolbar(self) -> str:
        rows = self._rows()
        if rows and self._selected_index < len(rows):
            enter_hint = (
                "[Enter ─ (read-only)]"
                if rows[self._selected_index]["readonly"]
                else "[Enter Toggle]"
            )
        else:
            enter_hint = "[Enter Toggle]"
        return f" [↑/↓ Navigate]  {enter_hint}  [b Back]  [r Refresh]  [q Quit] "

    def key_bindings(self) -> KeyBindings:
        kb = KeyBindings()

        @kb.add("up")
        def _(event: KeyPressEvent) -> None:  
            if self._selected_index > 0:
                self._selected_index -= 1

        @kb.add("down")
        def _(event: KeyPressEvent) -> None:  
            rows = self._rows()
            if self._selected_index < len(rows) - 1:
                self._selected_index += 1

        @kb.add("enter")
        def _(event: KeyPressEvent) -> None:  
            rows = self._rows()
            if not rows:
                return
            row = rows[self._selected_index]
            if not row["readonly"] and row["toggle"] is not None:
                toggle_fn: Callable[[], bool] = row["toggle"]
                toggle_fn()
                event.app.invalidate()

        @kb.add("b")
        @kb.add("escape")
        def _(event: KeyPressEvent) -> None:  
            from src.UI.screens.hubs_list import HubsListScreen
            self._controller.switch_to(HubsListScreen(self._controller))

        @kb.add("r")
        def _(event: KeyPressEvent) -> None:  
            event.app.invalidate()

        @kb.add("q")
        @kb.add("c-c")
        def _(event: KeyPressEvent) -> None:  
            event.app.exit()

        return kb