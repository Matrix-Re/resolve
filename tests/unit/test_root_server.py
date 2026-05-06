import json
from pathlib import Path

import pytest

from core.message import DNSQuery
from servers.root_server import RootServer, parse_args

from core.enums import ResponseStatus, RecordType, MessageType, ErrorCode
from core.constants import (
    DEFAULT_HOST,
    DEFAULT_ROOT_CONFIG_PATH,
    RESOLVER_DEFAULT_PORT,
    ROOT_DEFAULT_PORT,
)


def create_root_config(config_path: Path) -> None:
    config = {
        ".com": {"host": DEFAULT_HOST, "port": ROOT_DEFAULT_PORT},
        ".fr": {"host": DEFAULT_HOST, "port": 5304},
    }

    config_path.write_text(
        json.dumps(config),
        encoding="utf-8",
    )


@pytest.fixture
def root_server(tmp_path: Path) -> RootServer:
    config_path = tmp_path / "root.json"
    create_root_config(config_path)

    return RootServer(
        host=DEFAULT_HOST,
        port=RESOLVER_DEFAULT_PORT,
        config_path=str(config_path),
    )


def test_resolve_com_domain_returns_tld_server(root_server: RootServer) -> None:
    query = DNSQuery(
        message_type=MessageType.QUERY,
        domain="google.com",
        record_type=RecordType.A,
    )

    response = root_server.resolve(query)

    assert response.status == ResponseStatus.OK
    assert response.domain == ".com"
    assert response.record_type == RecordType.TLD
    assert response.value == f"{DEFAULT_HOST}:{ROOT_DEFAULT_PORT}"


def test_resolve_com_sub_domain_returns_tld_server(root_server: RootServer) -> None:
    query = DNSQuery(
        message_type=MessageType.QUERY,
        domain="maps.google.com",
        record_type=RecordType.A,
    )

    response = root_server.resolve(query)

    assert response.status == ResponseStatus.OK
    assert response.domain == ".com"
    assert response.record_type == RecordType.TLD
    assert response.value == f"{DEFAULT_HOST}:{ROOT_DEFAULT_PORT}"


def test_resolve_fr_domain_returns_tld_server(root_server: RootServer) -> None:
    query = DNSQuery(
        message_type=MessageType.QUERY,
        domain="free.fr",
        record_type=RecordType.A,
    )

    response = root_server.resolve(query)

    assert response.status == ResponseStatus.OK
    assert response.domain == ".fr"
    assert response.record_type == RecordType.TLD
    assert response.value == f"{DEFAULT_HOST}:5304"


def test_resolve_unknown_suffix_returns_error(root_server: RootServer) -> None:
    query = DNSQuery(
        message_type=MessageType.QUERY,
        domain="example.xyz",
        record_type=RecordType.A,
    )

    response = root_server.resolve(query)

    assert response.status == ResponseStatus.ERROR
    assert response.error_code in {ErrorCode.TLD_NOT_FOUND, ErrorCode.NOT_FOUND}


def test_resolve_invalid_tld_config_returns_error(tmp_path: Path) -> None:
    config_path = tmp_path / "root.json"
    config = {".com": {"host": DEFAULT_HOST}}

    config_path.write_text(
        json.dumps(config),
        encoding="utf-8",
    )

    server = RootServer(
        host=DEFAULT_HOST,
        port=RESOLVER_DEFAULT_PORT,
        config_path=str(config_path),
    )

    query = DNSQuery(
        message_type=MessageType.QUERY,
        domain="google.com",
        record_type=RecordType.A,
    )

    response = server.resolve(query)

    assert response.status == ResponseStatus.ERROR
    assert response.error_code == ErrorCode.INVALID_CONFIG


def test_handle_request_with_invalid_json_returns_error(
    root_server: RootServer,
) -> None:
    response = root_server.handle_request(b"{invalid-json")

    assert response.status == ResponseStatus.ERROR
    assert response.error_code == ErrorCode.INVALID_JSON


def test_handle_request_with_missing_field_returns_error(
    root_server: RootServer,
) -> None:
    payload = json.dumps(
        {
            "message_type": MessageType.QUERY,
            "domain": "google.com",
        }
    ).encode("utf-8")

    response = root_server.handle_request(payload)

    assert response.status == ResponseStatus.ERROR
    assert response.error_code == ErrorCode.INVALID_REQUEST


def test_parse_args_with_default_values(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "sys.argv",
        [
            "root_server.py",
        ],
    )

    args = parse_args()

    assert args.host == DEFAULT_HOST
    assert args.port == ROOT_DEFAULT_PORT
    assert args.config == DEFAULT_ROOT_CONFIG_PATH


def test_parse_args_with_custom_values(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "sys.argv",
        [
            "root_server.py",
            "--host",
            "0.0.0.0",
            "--port",
            "5403",
            "--config",
            "custom/root",
        ],
    )

    args = parse_args()

    assert args.host == "0.0.0.0"
    assert args.port == 5403
    assert args.config == "custom/root"
