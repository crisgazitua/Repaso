from src.Protocol.message import Message


def serialize_message(message: Message) -> str:
    if not message.parameters:
        return f"{message.message_type}."

    parameter_text = ";".join(
        f"{key}={value}" for key, value in message.parameters.items()
    )
    return f"{message.message_type}:{parameter_text}."
