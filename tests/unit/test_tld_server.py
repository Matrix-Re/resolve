import json
from pathlib import Path

import pytest

from core.message import DNSQuery
from core.enums import MessageType, RecordType, ResponseStatus, ErrorCode
from servers.tld_server import TLDServer
from core.config import load_json_file


def create_tld_config(config_path: Path) -> None:
    config = {
        "google.com": {"host": "127.0.0.1", "port": 5302},
        "amazon.com": {"host": "127.0.0.1", "port": 5303},
    }

    config_path.write_text(
        json.dumps(config),
        encoding="utf-8",
    )


@pytest.fixture
def tld_server(tmp_path: Path) -> TLDServer:
    config_path = tmp_path / "tld.json"
    create_tld_config(config_path)

    return TLDServer(
        host="127.0.0.1",
        port=5301,
        config_path=str(config_path),
    )


def test_load_config(tld_server: TLDServer) -> None:
    config = load_json_file(tld_server.config_path)

    assert config["google.com"]["host"] == "127.0.0.1"
    assert config["google.com"]["port"] == 5302
    assert config["amazon.com"]["host"] == "127.0.0.1"
    assert config["amazon.com"]["port"] == 5303


def test_resolve_domain_returns_authoritative_server(
    tld_server: TLDServer,
) -> None:
    query = DNSQuery(
        message_type=MessageType.QUERY,
        domain="google.com",
        record_type=RecordType.A,
    )

    response = tld_server.resolve(query)

    assert response.status == ResponseStatus.OK
    assert response.domain == "google.com"
    assert response.record_type == RecordType.AUTHORITATIVE
    assert response.value == "127.0.0.1:5302"


def test_resolve_sub_domain_returns_authoritative_server(
    tld_server: TLDServer,
) -> None:
    query = DNSQuery(
        message_type=MessageType.QUERY,
        domain="maps.google.com",
        record_type=RecordType.A,
    )

    response = tld_server.resolve(query)

    assert response.status == ResponseStatus.OK
    assert response.domain == "google.com"
    assert response.record_type == RecordType.AUTHORITATIVE
    assert response.value == "127.0.0.1:5302"


def test_resolve_nested_sub_domain_returns_authoritative_server(
    tld_server: TLDServer,
) -> None:
    query = DNSQuery(
        message_type=MessageType.QUERY,
        domain="example.maps.google.com",
        record_type=RecordType.A,
    )

    response = tld_server.resolve(query)

    assert response.status == ResponseStatus.OK
    assert response.domain == "google.com"
    assert response.value == "127.0.0.1:5302"


def test_resolve_unknown_domain_returns_error(
    tld_server: TLDServer,
) -> None:
    query = DNSQuery(
        message_type=MessageType.QUERY,
        domain="facebook.com",
        record_type=RecordType.A,
    )

    response = tld_server.resolve(query)

    assert response.status == ResponseStatus.ERROR
    assert response.error_code == ErrorCode.AUTHORITATIVE_NOT_FOUND


def test_load_missing_config_raises_file_not_found(tmp_path: Path) -> None:
    server = TLDServer(
        host="127.0.0.1",
        port=5301,
        config_path=str(tmp_path / "missing-tld.json"),
    )

    with pytest.raises(FileNotFoundError):
        load_json_file(server.config_path)


def test_load_invalid_config_raises_value_error(tmp_path: Path) -> None:
    config_path = tmp_path / "tld.json"
    config_path.write_text(
        json.dumps(["invalid", "config"]),
        encoding="utf-8",
    )

    server = TLDServer(
        host="127.0.0.1",
        port=5301,
        config_path=str(config_path),
    )

    with pytest.raises(ValueError):
        load_json_file(server.config_path)


def test_handle_request_with_invalid_json_returns_error(
    tld_server: TLDServer,
) -> None:
    response = tld_server.handle_request(b"{invalid-json")

    assert response.status == ResponseStatus.ERROR
    assert response.error_code == ErrorCode.INVALID_JSON


def test_handle_request_with_missing_field_returns_error(
    tld_server: TLDServer,
) -> None:
    payload = json.dumps(
        {
            "message_type": MessageType.QUERY,
            "domain": "google.com",
        }
    ).encode("utf-8")

    response = tld_server.handle_request(payload)

    assert response.status == ResponseStatus.ERROR
    assert response.error_code == ErrorCode.INVALID_REQUEST
