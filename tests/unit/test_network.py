import pytest

from core.network import parse_server_address
from core.constants import DEFAULT_HOST, TLD_DEFAULT_PORT


def test_parse_server_address() -> None:
    host, port = parse_server_address(f"{DEFAULT_HOST}:{TLD_DEFAULT_PORT}")

    assert host == DEFAULT_HOST
    assert port == TLD_DEFAULT_PORT


@pytest.mark.parametrize(
    "invalid_address",
    [
        "",
        DEFAULT_HOST,
        f":{TLD_DEFAULT_PORT}",
        f"{DEFAULT_HOST}:not-a-port",
    ],
)
def test_parse_server_address_with_invalid_address(invalid_address: str) -> None:
    with pytest.raises(ValueError):
        parse_server_address(invalid_address)
