from prompt_toolkit.formatted_text import FormattedText
from prompt_toolkit.key_binding import KeyBindings, KeyPressEvent
from prompt_toolkit.layout.containers import AnyContainer, HSplit, Window
from prompt_toolkit.layout.controls import FormattedTextControl
from src.UI.screens.base import Screen
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.UI.app import AppController


class HubsListScreen(Screen):
    def __init__(self, controller: 'AppController') -> None:  
        super().__init__(controller)
        self._selected_index: int = 0

    def _render(self) -> FormattedText:
        lines: list[tuple[str, str]] = []
        lines.append(("bold", "  Connected Hubs\n"))
        lines.append(("", "  " + "─" * 50 + "\n"))

        hub_names = sorted(self._controller.service.list_connected_homes())

        if not hub_names:
            lines.append(("", "  (no hubs currently connected)\n"))
            return FormattedText(lines)

        if self._selected_index >= len(hub_names):
            self._selected_index = max(0, len(hub_names) - 1)

        for i, name in enumerate(hub_names):
            house = self._controller.service.get_house(name)
            marker = "▶ " if i == self._selected_index else "  "
            style = "reverse" if i == self._selected_index else ""

            if house is None:
                summary = f"  {marker}{name:<15} (unavailable)\n"
            else:
                summary = (
                    f"  {marker}{name:<15} "
                    f"temp {house.temperature}°C  "
                    f"lights {sum(l.is_on for l in house.lights)}/{len(house.lights)}  "
                    f"alarm {house.alarm.status_text}\n"
                )
            lines.append((style, summary))

        return FormattedText(lines)

    def container(self) -> AnyContainer:
        return HSplit([
            Window(content=FormattedTextControl(text=self._render), wrap_lines=False),
        ])

    def bottom_toolbar(self) -> str:
        return (
            " [↑/↓ Navigate]  [Enter Inspect]  "
            "[c Credentials]  [r Refresh]  [q Quit] "
        )

    def key_bindings(self) -> KeyBindings:
        kb = KeyBindings()

        @kb.add("up")
        def _(event: KeyPressEvent) -> None:  
            if self._selected_index > 0:
                self._selected_index -= 1

        @kb.add("down")
        def _(event: KeyPressEvent) -> None:  
            hub_names = self._controller.service.list_connected_homes()
            if self._selected_index < len(hub_names) - 1:
                self._selected_index += 1

        @kb.add("enter")
        def _(event: KeyPressEvent) -> None:  
            hub_names = sorted(self._controller.service.list_connected_homes())
            if not hub_names:
                return
            home_name = hub_names[self._selected_index]
            from src.UI.screens.house_view import HouseViewScreen
            self._controller.switch_to(HouseViewScreen(self._controller, home_name))

        @kb.add("c")
        def _(event: KeyPressEvent) -> None:  
            from src.UI.screens.credentials import CredentialsScreen
            self._controller.switch_to(CredentialsScreen(self._controller))

        @kb.add("r")
        def _(event: KeyPressEvent) -> None:  
            event.app.invalidate()

        @kb.add("q")
        @kb.add("c-c")
        def _(event: KeyPressEvent) -> None:  
            event.app.exit()

        return kb