import pytest

from core.network import parse_server_address


def test_parse_server_address() -> None:
    host, port = parse_server_address("127.0.0.1:5302")

    assert host == "127.0.0.1"
    assert port == 5302


@pytest.mark.parametrize(
    "invalid_address",
    [
        "",
        "127.0.0.1",
        ":5302",
        "127.0.0.1:not-a-port",
    ],
)
def test_parse_server_address_with_invalid_address(invalid_address: str) -> None:
    with pytest.raises(ValueError):
        parse_server_address(invalid_address)
