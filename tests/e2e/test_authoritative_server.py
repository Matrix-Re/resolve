import json
from pathlib import Path

import pytest

from core.message import DNSQuery
from core.enums import MessageType, RecordType, ResponseStatus, ErrorCode
from servers.authoritative_server import AuthoritativeServer


def create_zone_file(zones_path: Path) -> None:
    zones_path.mkdir(parents=True, exist_ok=True)

    zone = {
        "domain": "google.com",
        "records": {
            "google.com": {
                "A": {
                    "value": "142.250.74.68",
                    "ttl": 300,
                },
                "AAAA": {
                    "value": "2001:4860:4860::8888",
                    "ttl": 300,
                },
            },
            "maps.google.com": {
                "A": {
                    "value": "142.250.74.100",
                    "ttl": 300,
                }
            },
            "example.maps.google.com": {
                "A": {
                    "value": "142.250.74.101",
                    "ttl": 120,
                }
            },
        },
    }

    (zones_path / "google.com.json").write_text(
        json.dumps(zone),
        encoding="utf-8",
    )


@pytest.fixture
def authoritative_server(tmp_path: Path) -> AuthoritativeServer:
    zones_path = tmp_path / "zones"
    create_zone_file(zones_path)

    return AuthoritativeServer(
        host="127.0.0.1",
        port=5302,
        zone_path=str(zones_path),
    )


def test_load_zone(authoritative_server: AuthoritativeServer) -> None:
    zone = authoritative_server.load_zone("google.com")

    assert zone["domain"] == "google.com"
    assert "google.com" in zone["records"]
    assert "maps.google.com" in zone["records"]


def test_resolve_root_domain_a_record(
    authoritative_server: AuthoritativeServer,
) -> None:
    query = DNSQuery(
        message_type=MessageType.QUERY,
        domain="google.com",
        record_type=RecordType.A,
    )

    response = authoritative_server.resolve(query)

    assert response.status == ResponseStatus.OK
    assert response.domain == "google.com"
    assert response.record_type == RecordType.A
    assert response.value == "142.250.74.68"
    assert response.ttl == 300


def test_resolve_sub_domain_a_record(
    authoritative_server: AuthoritativeServer,
) -> None:
    query = DNSQuery(
        message_type=MessageType.QUERY,
        domain="maps.google.com",
        record_type=RecordType.A,
    )

    response = authoritative_server.resolve(query)

    assert response.status == ResponseStatus.OK
    assert response.domain == "maps.google.com"
    assert response.record_type == RecordType.A
    assert response.value == "142.250.74.100"
    assert response.ttl == 300


def test_resolve_nested_sub_domain(
    authoritative_server: AuthoritativeServer,
) -> None:
    query = DNSQuery(
        message_type=MessageType.QUERY,
        domain="example.maps.google.com",
        record_type=RecordType.A,
    )

    response = authoritative_server.resolve(query)

    assert response.status == ResponseStatus.OK
    assert response.domain == "example.maps.google.com"
    assert response.value == "142.250.74.101"
    assert response.ttl == 120


def test_resolve_unknown_domain_returns_not_found(
    authoritative_server: AuthoritativeServer,
) -> None:
    query = DNSQuery(
        message_type=MessageType.QUERY,
        domain="unknown.google.com",
        record_type=RecordType.A,
    )

    response = authoritative_server.resolve(query)

    assert response.status == ResponseStatus.ERROR
    assert response.error_code == ErrorCode.NOT_FOUND


def test_resolve_unknown_record_type_returns_record_not_found(
    authoritative_server: AuthoritativeServer,
) -> None:
    query = DNSQuery(
        message_type=MessageType.QUERY,
        domain="maps.google.com",
        record_type=RecordType.AAAA,
    )

    response = authoritative_server.resolve(query)

    assert response.status == ResponseStatus.ERROR
    assert response.error_code == "RECORD_NOT_FOUND"


def test_load_unknown_zone_raises_file_not_found(
    authoritative_server: AuthoritativeServer,
) -> None:
    with pytest.raises(FileNotFoundError):
        authoritative_server.load_zone("facebook.com")
