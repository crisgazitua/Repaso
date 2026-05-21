from typing import cast

from src.Credentials.credential import Credential
from src.Credentials.in_memory_credential_store import InMemoryCredentialStore
from src.Protocol import MESSAGE_TERMINATOR, MSG_ACC, MSG_ERR, MSG_GS, MSG_REF, Message
from src.Protocol.message import MessageType
from src.Server import CleverHomeProtocolHandler, SessionContext


def _response_text(message_type: str) -> str:
    return f"{message_type}{MESSAGE_TERMINATOR}"


def _build_handler() -> CleverHomeProtocolHandler:
    store = InMemoryCredentialStore(
        initial_credentials=[
            Credential(username="u1", password="p1", home_name="home1"),
            Credential(username="u2", password="p2", home_name="home2"),
        ]
    )
    return CleverHomeProtocolHandler(credential_store=store)


def test_non_hl_before_auth_is_refused() -> None:
    handler = _build_handler()
    session = SessionContext()
    response, should_close = handler.process_incoming("GS.", session)
    assert response == _response_text(MSG_REF)
    assert should_close is True


def test_hl_valid_credentials_returns_acc() -> None:
    handler = _build_handler()
    session = SessionContext()
    response, should_close = handler.process_incoming(
        "HL:USR=u1;PWD=p1;HOM=home1;TT=20.", session
    )
    assert response == _response_text(MSG_ACC)
    assert should_close is False
    assert session.authenticated is True


def test_hl_invalid_credentials_returns_ref() -> None:
    handler = _build_handler()
    session = SessionContext()
    response, should_close = handler.process_incoming(
        "HL:USR=u1;PWD=wrong;HOM=home1;TT=20.", session
    )
    assert response == _response_text(MSG_REF)
    assert should_close is True


def test_duplicate_home_connection_is_refused() -> None:
    handler = _build_handler()
    session_one = SessionContext()
    session_two = SessionContext()

    first_response, _ = handler.process_incoming(
        "HL:USR=u1;PWD=p1;HOM=home1;TT=20.", session_one
    )
    second_response, should_close = handler.process_incoming(
        "HL:USR=u1;PWD=p1;HOM=home1;TT=20.", session_two
    )
    assert first_response == _response_text(MSG_ACC)
    assert second_response == _response_text(MSG_REF)
    assert should_close is True


def test_gs_returns_su_after_authentication() -> None:
    handler = _build_handler()
    session = SessionContext()
    handler.process_incoming("HL:USR=u1;PWD=p1;HOM=home1;TT=20.", session)
    response, should_close = handler.process_incoming("GS.", session)
    assert response.startswith("SU:")
    assert response.endswith(".")
    assert should_close is False


def test_connected_hub_domain_actions_update_state() -> None:
    handler = _build_handler()
    session = SessionContext()
    handler.process_incoming("HL:USR=u1;PWD=p1;HOM=home1;TT=20.", session)

    hub = handler.get_hub("home1")
    assert hub is not None

    assert hub.set_light(0, True) is True
    assert hub.set_door_lock(2, True) is True
    assert hub.set_alarm(True) is True
    assert hub.set_hvac_mode("cool") is True

    response, _ = handler.process_incoming("GS.", session)
    assert "LS0=1" in response
    assert "DS2=1" in response
    assert "AS=1" in response
    assert "CS=1" in response
    assert "HS=0" in response


def test_send_message_returns_response_message() -> None:
    handler = _build_handler()
    session = SessionContext()
    handler.process_incoming("HL:USR=u1;PWD=p1;HOM=home1;TT=20.", session)

    response = handler.send_message(
        "home1", Message(message_type=cast(MessageType, MSG_GS))
    )
    assert response.message_type == "SU"
    assert "TR" in response.parameters


def test_ss_rejects_ao_zero() -> None:
    handler = _build_handler()
    session = SessionContext()
    handler.process_incoming("HL:USR=u1;PWD=p1;HOM=home1;TT=20.", session)
    response, should_close = handler.process_incoming("SS:AO=0.", session)
    assert response == _response_text(MSG_ERR)
    assert should_close is False


def test_ss_rejects_heater_chiller_enabled_together() -> None:
    handler = _build_handler()
    session = SessionContext()
    handler.process_incoming("HL:USR=u1;PWD=p1;HOM=home1;TT=20.", session)
    response, should_close = handler.process_incoming("SS:HS=1;CS=1.", session)
    assert response == _response_text(MSG_ERR)
    assert should_close is False
