from dataclasses import dataclass, field
from typing import Literal

ParameterMap = dict[str, str]

MessageType = Literal["HL", "GS", "SS", "ACC", "REF", "SU", "OK", "ERR"]

REQUEST_TYPES: set[str] = {"HL", "GS", "SS"}
RESPONSE_TYPES: set[str] = {"ACC", "REF", "SU", "OK", "ERR"}


@dataclass(frozen=True)
class Message:
    message_type: MessageType
    parameters: ParameterMap = field(default_factory=dict)

    @property
    def is_request(self) -> bool:
        return self.message_type in REQUEST_TYPES

    @property
    def is_response(self) -> bool:
        return self.message_type in RESPONSE_TYPES
