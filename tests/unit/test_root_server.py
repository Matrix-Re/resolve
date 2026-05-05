import json
from pathlib import Path

import pytest

from core.message import DNSQuery
from servers.root_server import RootServer


def create_root_config(config_path: Path) -> None:
    config = {
        ".com": {"host": "127.0.0.1", "port": 5301},
        ".fr": {"host": "127.0.0.1", "port": 5304},
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
        host="127.0.0.1",
        port=5300,
        config_path=str(config_path),
    )


def test_resolve_com_domain_returns_tld_server(root_server: RootServer) -> None:
    query = DNSQuery(
        message_type="query",
        domain="google.com",
        record_type="A",
    )

    response = root_server.resolve(query)

    assert response.status == "ok"
    assert response.domain == ".com"
    assert response.record_type == "TLD"
    assert response.value == "127.0.0.1:5301"


def test_resolve_com_sub_domain_returns_tld_server(root_server: RootServer) -> None:
    query = DNSQuery(
        message_type="query",
        domain="maps.google.com",
        record_type="A",
    )

    response = root_server.resolve(query)

    assert response.status == "ok"
    assert response.domain == ".com"
    assert response.record_type == "TLD"
    assert response.value == "127.0.0.1:5301"


def test_resolve_fr_domain_returns_tld_server(root_server: RootServer) -> None:
    query = DNSQuery(
        message_type="query",
        domain="free.fr",
        record_type="A",
    )

    response = root_server.resolve(query)

    assert response.status == "ok"
    assert response.domain == ".fr"
    assert response.record_type == "TLD"
    assert response.value == "127.0.0.1:5304"


def test_resolve_unknown_suffix_returns_error(root_server: RootServer) -> None:
    query = DNSQuery(
        message_type="query",
        domain="example.xyz",
        record_type="A",
    )

    response = root_server.resolve(query)

    assert response.status == "error"
    assert response.error_code in {"TLD_NOT_FOUND", "NOT_FOUND"}


def test_resolve_invalid_tld_config_returns_error(tmp_path: Path) -> None:
    config_path = tmp_path / "root.json"
    config = {".com": {"host": "127.0.0.1"}}

    config_path.write_text(
        json.dumps(config),
        encoding="utf-8",
    )

    server = RootServer(
        host="127.0.0.1",
        port=5300,
        config_path=str(config_path),
    )

    query = DNSQuery(
        message_type="query",
        domain="google.com",
        record_type="A",
    )

    response = server.resolve(query)

    assert response.status == "error"
    assert response.error_code in {"INVALID_CONFIG", "INVALID_TLD_CONFIG"}


def test_handle_request_with_invalid_json_returns_error(
    root_server: RootServer,
) -> None:
    response = root_server.handle_request(b"{invalid-json")

    assert response.status == "error"
    assert response.error_code == "INVALID_JSON"


def test_handle_request_with_missing_field_returns_error(
    root_server: RootServer,
) -> None:
    payload = json.dumps(
        {
            "message_type": "query",
            "domain": "google.com",
        }
    ).encode("utf-8")

    response = root_server.handle_request(payload)

    assert response.status == "error"
    assert response.error_code == "INVALID_REQUEST"
