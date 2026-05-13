from typing import cast

from src.Protocol.message import Message, MessageType, REQUEST_TYPES, RESPONSE_TYPES


class ProtocolParseError(ValueError):
    """Raised when a protocol message is malformed."""


def parse_message(raw: str) -> Message:
    text = raw.strip()
    if not text.endswith("."):
        raise ProtocolParseError("Message must end with '.'")

    without_period = text[:-1]
    if not without_period:
        raise ProtocolParseError("Message cannot be empty")

    if ":" in without_period:
        message_type, parameter_block = without_period.split(":", 1)
    else:
        message_type, parameter_block = without_period, ""

    if message_type not in REQUEST_TYPES and message_type not in RESPONSE_TYPES:
        raise ProtocolParseError(f"Unsupported message type: {message_type}")

    parameters = _parse_parameters(parameter_block)
    _validate_semantics(message_type, parameters)
    typed_message_type = cast(MessageType, message_type)
    return Message(message_type=typed_message_type, parameters=parameters)


def _parse_parameters(parameter_block: str) -> dict[str, str]:
    if parameter_block == "":
        return {}

    parts = parameter_block.split(";")
    if any(part == "" for part in parts):
        raise ProtocolParseError("Invalid parameter list formatting")

    parsed: dict[str, str] = {}
    for part in parts:
        if "=" not in part:
            raise ProtocolParseError(f"Invalid parameter expression: {part}")
        key, value = part.split("=", 1)
        if not key or not value:
            raise ProtocolParseError(f"Invalid key/value pair: {part}")
        parsed[key] = value
    return parsed


def _validate_semantics(message_type: str, parameters: dict[str, str]) -> None:
    if message_type in {"ACC", "REF", "OK", "ERR", "GS"} and parameters:
        raise ProtocolParseError(f"{message_type} does not accept parameters")

    if message_type == "HL":
        expected = {"USR", "PWD", "HOM", "TT"}
        if set(parameters.keys()) != expected:
            raise ProtocolParseError("HL must include USR, PWD, HOM, TT only")
        _validate_integer("TT", parameters["TT"])

    if message_type == "SS":
        if not parameters:
            raise ProtocolParseError("SS requires at least one state parameter")
        for key, value in parameters.items():
            _validate_state_assignment(key, value, allow_read_only=False)

    if message_type == "SU":
        if not parameters:
            raise ProtocolParseError("SU requires at least one state parameter")
        for key, value in parameters.items():
            _validate_state_assignment(key, value, allow_read_only=True)


def _validate_state_assignment(key: str, value: str, allow_read_only: bool) -> None:
    if key == "TR":
        if not allow_read_only:
            raise ProtocolParseError("TR is read-only and cannot be set via SS")
        _validate_integer(key, value)
        return

    if key.startswith("DS") or key.startswith("LS") or key.startswith("PS"):
        suffix = key[2:]
        if not suffix.isdigit() or int(suffix) < 1:
            raise ProtocolParseError(f"Invalid indexed state key: {key}")
        if key.startswith("PS") and not allow_read_only:
            raise ProtocolParseError("PS[N] is read-only and cannot be set via SS")
        _validate_binary(key, value)
        return

    if key in {"AS", "AO", "HS", "CS"}:
        _validate_binary(key, value)
        return

    raise ProtocolParseError(f"Unsupported state key: {key}")


def _validate_binary(key: str, value: str) -> None:
    if value not in {"0", "1"}:
        raise ProtocolParseError(f"{key} must be either 0 or 1")


def _validate_integer(key: str, value: str) -> None:
    try:
        int(value)
    except ValueError as exc:
        raise ProtocolParseError(f"{key} must be an integer") from exc
