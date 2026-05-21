from typing import cast

from src.Protocol.constants import (
    BINARY_ONE,
    BINARY_ZERO,
    KEY_AO,
    KEY_AS,
    KEY_CS,
    KEY_HOM,
    KEY_HS,
    KEY_PWD,
    KEY_TR,
    KEY_TT,
    KEY_USR,
    KEY_VALUE_SEPARATOR,
    MESSAGE_TERMINATOR,
    MSG_ACC,
    MSG_ERR,
    MSG_GS,
    MSG_HL,
    MSG_OK,
    MSG_REF,
    MSG_SS,
    MSG_SU,
    PARAMETER_SEPARATOR,
    PREFIX_DS,
    PREFIX_LS,
    PREFIX_PS,
    TYPE_PARAMETER_SEPARATOR,
)
from src.Protocol.message import Message, MessageType, REQUEST_TYPES, RESPONSE_TYPES


class ProtocolParseError(ValueError):
    pass


def parse_message(raw: str) -> Message:
    text = raw.strip()
    if not text.endswith(MESSAGE_TERMINATOR):
        raise ProtocolParseError("Message must end with terminator")

    body = text[: -len(MESSAGE_TERMINATOR)]
    if not body:
        raise ProtocolParseError("Message cannot be empty")

    if TYPE_PARAMETER_SEPARATOR in body:
        message_type, parameter_block = body.split(TYPE_PARAMETER_SEPARATOR, 1)
    else:
        message_type, parameter_block = body, ""

    if message_type not in REQUEST_TYPES and message_type not in RESPONSE_TYPES:
        raise ProtocolParseError(f"Unsupported message type: {message_type}")

    parameters = _parse_parameters(parameter_block)
    _validate_message(cast(MessageType, message_type), parameters)
    return Message(message_type=cast(MessageType, message_type), parameters=parameters)


def serialize_message(message: Message) -> str:
    if not message.parameters:
        return f"{message.message_type}{MESSAGE_TERMINATOR}"

    parameter_text = PARAMETER_SEPARATOR.join(
        f"{key}{KEY_VALUE_SEPARATOR}{value}" for key, value in message.parameters.items()
    )
    return f"{message.message_type}{TYPE_PARAMETER_SEPARATOR}{parameter_text}{MESSAGE_TERMINATOR}"


def _parse_parameters(parameter_block: str) -> dict[str, str]:
    if not parameter_block:
        return {}

    parsed: dict[str, str] = {}
    for part in parameter_block.split(PARAMETER_SEPARATOR):
        if KEY_VALUE_SEPARATOR not in part:
            raise ProtocolParseError(f"Invalid parameter expression: {part}")
        key, value = part.split(KEY_VALUE_SEPARATOR, 1)
        if not key or not value:
            raise ProtocolParseError(f"Invalid key/value pair: {part}")
        parsed[key] = value
    return parsed


def _validate_message(message_type: MessageType, parameters: dict[str, str]) -> None:
    if message_type in {MSG_ACC, MSG_REF, MSG_OK, MSG_ERR, MSG_GS}:
        if parameters:
            raise ProtocolParseError(f"{message_type} does not accept parameters")
        return

    if message_type == MSG_HL:
        _validate_hl(parameters)
        return

    if message_type == MSG_SS:
        _validate_state_parameters(parameters, allow_read_only=False)
        return

    if message_type == MSG_SU:
        _validate_state_parameters(parameters, allow_read_only=True)


def _validate_hl(parameters: dict[str, str]) -> None:
    expected = {KEY_USR, KEY_PWD, KEY_HOM, KEY_TT}
    if set(parameters.keys()) != expected:
        raise ProtocolParseError("HL must include USR, PWD, HOM, TT only")
    _validate_integer(KEY_TT, parameters[KEY_TT])


def _validate_state_parameters(parameters: dict[str, str], allow_read_only: bool) -> None:
    if not parameters:
        raise ProtocolParseError("State message requires at least one state parameter")

    for key, value in parameters.items():
        if key == KEY_TR:
            if not allow_read_only:
                raise ProtocolParseError("TR is read-only and cannot be set via SS")
            _validate_integer(key, value)
            continue

        if key.startswith(PREFIX_DS) or key.startswith(PREFIX_LS) or key.startswith(PREFIX_PS):
            _validate_indexed_state_key(key, allow_read_only)
            _validate_binary(key, value)
            continue

        if key in {KEY_AS, KEY_AO, KEY_HS, KEY_CS}:
            _validate_binary(key, value)
            continue

        raise ProtocolParseError(f"Unsupported state key: {key}")


def _validate_indexed_state_key(key: str, allow_read_only: bool) -> None:
    suffix = key[2:]
    if not suffix.isdigit():
        raise ProtocolParseError(f"Invalid indexed state key: {key}")
    if key.startswith(PREFIX_PS) and not allow_read_only:
        raise ProtocolParseError("PS[N] is read-only and cannot be set via SS")


def _validate_binary(key: str, value: str) -> None:
    if value not in {BINARY_ZERO, BINARY_ONE}:
        raise ProtocolParseError(f"{key} must be either 0 or 1")


def _validate_integer(key: str, value: str) -> None:
    try:
        int(value)
    except ValueError as exc:
        raise ProtocolParseError(f"{key} must be an integer") from exc
