import pytest
from src.Protocol import ProtocolParseError, parse_message, serialize_message


def test_parse_hl_valid() -> None:
    msg = parse_message("HL:USR=u;PWD=p;HOM=h;TT=20.")
    assert msg.message_type == "HL"
    assert msg.parameters == {"USR": "u", "PWD": "p", "HOM": "h", "TT": "20"}


def test_parse_gs_valid() -> None:
    msg = parse_message("GS.")
    assert msg.message_type == "GS"
    assert msg.parameters == {}


def test_parse_missing_period_fails() -> None:
    with pytest.raises(ProtocolParseError):
        parse_message("GS")


def test_parse_hl_missing_param_fails() -> None:
    with pytest.raises(ProtocolParseError):
        parse_message("HL:USR=u;PWD=p;HOM=h.")


def test_parse_ss_readonly_tr_fails() -> None:
    with pytest.raises(ProtocolParseError):
        parse_message("SS:TR=20.")


def test_parse_ss_readonly_ps_fails() -> None:
    with pytest.raises(ProtocolParseError):
        parse_message("SS:PS1=1.")


def test_parse_ss_valid_with_zero_index() -> None:
    msg = parse_message("SS:DS0=1;LS1=0;AS=1.")
    assert msg.message_type == "SS"


def test_parse_su_valid() -> None:
    msg = parse_message("SU:TR=20;DS0=1;PS1=0;AS=1;AO=0;HS=1;CS=0.")
    assert msg.message_type == "SU"


def test_serialize_no_params() -> None:
    msg = parse_message("OK.")
    assert serialize_message(msg) == "OK."


def test_serialize_with_params() -> None:
    msg = parse_message("SS:DS1=1;LS1=0.")
    assert serialize_message(msg) == "SS:DS1=1;LS1=0."
