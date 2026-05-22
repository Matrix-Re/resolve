import socket
import pytest

from core.enums import MessageType, RecordType, ResponseStatus, ErrorCode
from core.constants import (
    DEFAULT_HOST,
    RESOLVER_DEFAULT_PORT,
    ROOT_DEFAULT_PORT,
    AUTHORITATIVE_DEFAULT_PORT,
    TLD_DEFAULT_PORT,
)
from core.message import DNSQuery, DNSResponse
from resolver.recursive_resolver import RecursiveResolver, parse_args


def create_resolver() -> RecursiveResolver:
    return RecursiveResolver(
        host=DEFAULT_HOST,
        port=RESOLVER_DEFAULT_PORT,
        root_host=DEFAULT_HOST,
        root_port=ROOT_DEFAULT_PORT,
        timeout=1,
    )


def test_resolver_calls_root_tld_and_authoritative_in_order(monkeypatch) -> None:
    resolver = create_resolver()

    query = DNSQuery(
        message_type=MessageType.QUERY,
        domain="maps.google.com",
        record_type=RecordType.A,
    )

    calls = []

    def fake_query_server(query: DNSQuery, host: str, port: int) -> DNSResponse:
        calls.append((host, port))

        if port == ROOT_DEFAULT_PORT:
            return DNSResponse(
                message_type=MessageType.RESPONSE,
                status=ResponseStatus.OK,
                domain=".com",
                record_type=RecordType.TLD,
                value=f"{DEFAULT_HOST}:{TLD_DEFAULT_PORT}",
            )

        if port == TLD_DEFAULT_PORT:
            return DNSResponse(
                message_type=MessageType.RESPONSE,
                status=ResponseStatus.OK,
                domain="google.com",
                record_type=RecordType.AUTHORITATIVE,
                value=f"{DEFAULT_HOST}:{AUTHORITATIVE_DEFAULT_PORT}",
            )

        if port == AUTHORITATIVE_DEFAULT_PORT:
            return DNSResponse(
                message_type=MessageType.RESPONSE,
                status=ResponseStatus.OK,
                domain="maps.google.com",
                record_type=RecordType.A,
                value="142.250.74.100",
                ttl=300,
            )

        raise AssertionError(f"Unexpected server call: {host}:{port}")

    monkeypatch.setattr(resolver, "query_server", fake_query_server)

    response = resolver.resolve(query)

    assert calls == [
        (DEFAULT_HOST, ROOT_DEFAULT_PORT),
        (DEFAULT_HOST, TLD_DEFAULT_PORT),
        (DEFAULT_HOST, AUTHORITATIVE_DEFAULT_PORT),
    ]

    assert response.status == ResponseStatus.OK
    assert response.domain == "maps.google.com"
    assert response.record_type == RecordType.A
    assert response.value == "142.250.74.100"
    assert response.ttl == 300


def test_resolver_stops_if_root_returns_error(monkeypatch) -> None:
    resolver = create_resolver()

    query = DNSQuery(
        message_type=MessageType.QUERY,
        domain="unknown.xyz",
        record_type=RecordType.A,
    )

    calls = []

    def fake_query_server(query: DNSQuery, host: str, port: int) -> DNSResponse:
        calls.append((host, port))
        return DNSResponse(
            message_type=MessageType.RESPONSE,
            status=ResponseStatus.ERROR,
            error_code=ErrorCode.TLD_NOT_FOUND,
            error_message="No TLD server found",
        )

    monkeypatch.setattr(resolver, "query_server", fake_query_server)

    response = resolver.resolve(query)

    assert calls == [(DEFAULT_HOST, ROOT_DEFAULT_PORT)]
    assert response.status == ResponseStatus.ERROR
    assert response.error_code == ErrorCode.SERVER_ERROR


def test_resolver_stops_if_tld_returns_error(monkeypatch) -> None:
    resolver = create_resolver()

    query = DNSQuery(
        message_type=MessageType.QUERY,
        domain="facebook.com",
        record_type=RecordType.A,
    )

    calls = []

    def fake_query_server(query: DNSQuery, host: str, port: int) -> DNSResponse:
        calls.append((host, port))

        if port == ROOT_DEFAULT_PORT:
            return DNSResponse(
                message_type=MessageType.RESPONSE,
                status=ResponseStatus.OK,
                domain=".com",
                record_type=RecordType.TLD,
                value=f"{DEFAULT_HOST}:{TLD_DEFAULT_PORT}",
            )

        if port == TLD_DEFAULT_PORT:
            return DNSResponse(
                message_type=MessageType.RESPONSE,
                status=ResponseStatus.ERROR,
                error_code=ErrorCode.AUTHORITATIVE_NOT_FOUND,
                error_message="No authoritative server found",
            )

        raise AssertionError("Authoritative server should not be called")

    monkeypatch.setattr(resolver, "query_server", fake_query_server)

    response = resolver.resolve(query)

    assert calls == [
        (DEFAULT_HOST, ROOT_DEFAULT_PORT),
        (DEFAULT_HOST, TLD_DEFAULT_PORT),
    ]

    assert response.status == ResponseStatus.ERROR
    assert response.error_code == ErrorCode.AUTHORITATIVE_NOT_FOUND


def test_response_from_dict_builds_dns_response() -> None:
    resolver = create_resolver()

    response = resolver.response_from_dict(
        {
            "message_type": MessageType.RESPONSE,
            "status": ResponseStatus.OK,
            "domain": "maps.google.com",
            "record_type": RecordType.A,
            "value": "142.250.74.100",
            "ttl": 300,
        }
    )

    assert response.message_type == MessageType.RESPONSE
    assert response.status == ResponseStatus.OK
    assert response.domain == "maps.google.com"
    assert response.record_type == RecordType.A
    assert response.value == "142.250.74.100"
    assert response.ttl == 300


class FakeSocketTimeout:
    def settimeout(self, timeout: int) -> None:
        pass

    def sendto(self, payload: bytes, address: tuple[str, int]) -> None:
        pass

    def recvfrom(self, buffer_size: int) -> tuple[bytes, tuple[str, int]]:
        raise socket.timeout

    def close(self) -> None:
        pass


def test_query_server_returns_error_on_timeout(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    resolver = create_resolver()

    monkeypatch.setattr(
        socket,
        "socket",
        lambda *args, **kwargs: FakeSocketTimeout(),
    )

    query = DNSQuery(
        message_type=MessageType.QUERY,
        domain="maps.google.com",
        record_type=RecordType.A,
    )

    response = resolver.query_server(
        query=query,
        host=DEFAULT_HOST,
        port=AUTHORITATIVE_DEFAULT_PORT,
    )

    assert response.status == ResponseStatus.ERROR
    assert response.error_code == ErrorCode.SERVER_ERROR
    assert (
        f"Timeout while contacting server {DEFAULT_HOST}:{AUTHORITATIVE_DEFAULT_PORT}"
        in response.error_message
    )


class FakeSocketInvalidJson:
    def settimeout(self, timeout: int) -> None:
        pass

    def sendto(self, payload: bytes, address: tuple[str, int]) -> None:
        pass

    def recvfrom(self, buffer_size: int) -> tuple[bytes, tuple[str, int]]:
        return b"{invalid-json", (DEFAULT_HOST, AUTHORITATIVE_DEFAULT_PORT)

    def close(self) -> None:
        pass


def test_query_server_returns_error_on_invalid_json_response(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    resolver = create_resolver()

    monkeypatch.setattr(
        socket,
        "socket",
        lambda *args, **kwargs: FakeSocketInvalidJson(),
    )

    query = DNSQuery(
        message_type=MessageType.QUERY,
        domain="maps.google.com",
        record_type=RecordType.A,
    )

    response = resolver.query_server(
        query=query,
        host=DEFAULT_HOST,
        port=AUTHORITATIVE_DEFAULT_PORT,
    )

    assert response.status == ResponseStatus.ERROR
    assert response.error_code == ErrorCode.INVALID_JSON
    assert (
        f"Invalid JSON response from server {DEFAULT_HOST}:{AUTHORITATIVE_DEFAULT_PORT}"
        in response.error_message
    )


def test_extract_next_server_raises_error_when_value_is_missing() -> None:
    resolver = create_resolver()

    response = DNSResponse(
        message_type=MessageType.RESPONSE,
        status=ResponseStatus.OK,
        domain=".com",
        record_type=RecordType.TLD,
        value=None,
        ttl=None,
    )

    with pytest.raises(ValueError, match="Missing server address in DNS response"):
        resolver.extract_next_server(response)


def test_parse_args_with_default_values(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "sys.argv",
        [
            "recursive_resolver.py",
        ],
    )

    args = parse_args()

    assert args.host == DEFAULT_HOST
    assert args.port == RESOLVER_DEFAULT_PORT
    assert args.root_host == DEFAULT_HOST
    assert args.root_port == ROOT_DEFAULT_PORT


def test_parse_args_with_custom_values(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "sys.argv",
        [
            "recursive_resolver.py",
            "--host",
            "0.0.0.0",
            "--port",
            "5400",
            "--root-host",
            DEFAULT_HOST,
            "--root-port",
            "5403",
        ],
    )

    args = parse_args()

    assert args.host == "0.0.0.0"
    assert args.port == 5400
    assert args.root_host == DEFAULT_HOST
    assert args.root_port == 5403


# -------------------
# ROOT FALLBACK TESTS
# -------------------


def test_query_root_servers_fallback_to_second_root(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    first_root_port = 5301
    second_root_port = 5311

    resolver = RecursiveResolver(
        host=DEFAULT_HOST,
        port=RESOLVER_DEFAULT_PORT,
        root_host=DEFAULT_HOST,
        root_port=first_root_port,
        roots=[
            (DEFAULT_HOST, first_root_port),
            (DEFAULT_HOST, second_root_port),
        ],
        timeout=1,
    )

    query = DNSQuery(
        message_type=MessageType.QUERY,
        domain="maps.google.com",
        record_type=RecordType.A,
    )

    calls = []

    def fake_query_server(query: DNSQuery, host: str, port: int) -> DNSResponse:
        calls.append((host, port))

        if port == first_root_port:
            return DNSResponse(
                message_type=MessageType.RESPONSE,
                status=ResponseStatus.ERROR,
                error_code=ErrorCode.SERVER_ERROR,
                error_message="Root server unavailable",
            )

        if port == second_root_port:
            return DNSResponse(
                message_type=MessageType.RESPONSE,
                status=ResponseStatus.OK,
                domain=".com",
                record_type=RecordType.TLD,
                value=f"{DEFAULT_HOST}:{TLD_DEFAULT_PORT}",
            )

        raise AssertionError(f"Unexpected root server call: {host}:{port}")

    monkeypatch.setattr(resolver, "query_server", fake_query_server)

    response = resolver.query_root_servers(query)

    assert calls == [
        (DEFAULT_HOST, first_root_port),
        (DEFAULT_HOST, second_root_port),
    ]

    assert response.status == ResponseStatus.OK
    assert response.domain == ".com"
    assert response.record_type == RecordType.TLD
    assert response.value == f"{DEFAULT_HOST}:{TLD_DEFAULT_PORT}"


def test_query_root_servers_returns_error_when_all_roots_fail(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    first_root_port = 5301
    second_root_port = 5311

    resolver = RecursiveResolver(
        host=DEFAULT_HOST,
        port=RESOLVER_DEFAULT_PORT,
        root_host=DEFAULT_HOST,
        root_port=first_root_port,
        roots=[
            (DEFAULT_HOST, first_root_port),
            (DEFAULT_HOST, second_root_port),
        ],
        timeout=1,
    )

    query = DNSQuery(
        message_type=MessageType.QUERY,
        domain="maps.google.com",
        record_type=RecordType.A,
    )

    calls = []

    def fake_query_server(query: DNSQuery, host: str, port: int) -> DNSResponse:
        calls.append((host, port))

        return DNSResponse(
            message_type=MessageType.RESPONSE,
            status=ResponseStatus.ERROR,
            error_code=ErrorCode.SERVER_ERROR,
            error_message="Root server unavailable",
        )

    monkeypatch.setattr(resolver, "query_server", fake_query_server)

    response = resolver.query_root_servers(query)

    assert calls == [
        (DEFAULT_HOST, first_root_port),
        (DEFAULT_HOST, second_root_port),
    ]

    assert response.status == ResponseStatus.ERROR
    assert response.error_code == ErrorCode.SERVER_ERROR
    assert response.error_message == "All Root servers are unavailable"
