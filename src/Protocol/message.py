from dataclasses import dataclass, field
from typing import Literal

from src.Protocol.constants import (
    MSG_ACC,
    MSG_ERR,
    MSG_GS,
    MSG_HL,
    MSG_OK,
    MSG_REF,
    MSG_SS,
    MSG_SU,
)

ParameterMap = dict[str, str]

MessageType = Literal[
    "HL",
    "GS",
    "SS",
    "ACC",
    "REF",
    "SU",
    "OK",
    "ERR",
]

REQUEST_TYPES: set[str] = {MSG_HL, MSG_GS, MSG_SS}
RESPONSE_TYPES: set[str] = {MSG_ACC, MSG_REF, MSG_SU, MSG_OK, MSG_ERR}


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
