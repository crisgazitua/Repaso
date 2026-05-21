from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout.containers import AnyContainer

if TYPE_CHECKING:
    from src.UI.app import AppController


class Screen(ABC):
    def __init__(self, controller: "AppController") -> None:
        self._controller = controller

    @abstractmethod
    def container(self) -> AnyContainer: ...

    @abstractmethod
    def key_bindings(self) -> KeyBindings: ...

    @abstractmethod
    def bottom_toolbar(self) -> str: ...