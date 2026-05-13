from abc import ABC, abstractmethod


class Command(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        """The keyword the operator types to invoke this command."""

    @property
    @abstractmethod
    def description(self) -> str:
        """A short, single-line description shown in the help menu."""

    @abstractmethod
    def execute(self, arguments: list[str]) -> str:
        """Execute the command with the given arguments.

        Args:
            arguments: The whitespace-separated tokens after the command name.

        Returns:
            A human-readable string to display to the operator.
        """
