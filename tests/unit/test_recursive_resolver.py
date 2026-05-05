from core.enums import MessageType, RecordType, ResponseStatus, ErrorCode
from core.message import DNSQuery, DNSResponse
from resolver.recursive_resolver import RecursiveResolver


def create_resolver() -> RecursiveResolver:
    return RecursiveResolver(
        host="127.0.0.1",
        port=5300,
        root_host="127.0.0.1",
        root_port=5303,
        timeout=1,
    )


def test_resolver_calls_root_tld_and_authoritative_in_order(monkeypatch) -> None:
    resolver = create_resolver()

    query = DNSQuery(
        message_type="query",
        domain="maps.google.com",
        record_type="A",
    )

    calls = []

    def fake_query_server(query: DNSQuery, host: str, port: int) -> DNSResponse:
        calls.append((host, port))

        if port == 5303:
            return DNSResponse(
                message_type=MessageType.RESPONSE,
                status=ResponseStatus.OK,
                domain=".com",
                record_type=RecordType.TLD,
                value="127.0.0.1:5301",
            )

        if port == 5301:
            return DNSResponse(
                message_type=MessageType.RESPONSE,
                status=ResponseStatus.OK,
                domain="google.com",
                record_type=RecordType.AUTHORITATIVE,
                value="127.0.0.1:5302",
            )

        if port == 5302:
            return DNSResponse(
                message_type=MessageType.RESPONSE,
                status=ResponseStatus.OK,
                domain="maps.google.com",
                record_type="A",
                value="142.250.74.100",
                ttl=300,
            )

        raise AssertionError(f"Unexpected server call: {host}:{port}")

    monkeypatch.setattr(resolver, "query_server", fake_query_server)

    response = resolver.resolve(query)

    assert calls == [
        ("127.0.0.1", 5303),
        ("127.0.0.1", 5301),
        ("127.0.0.1", 5302),
    ]

    assert response.status == ResponseStatus.OK
    assert response.domain == "maps.google.com"
    assert response.record_type == "A"
    assert response.value == "142.250.74.100"
    assert response.ttl == 300


def test_resolver_stops_if_root_returns_error(monkeypatch) -> None:
    resolver = create_resolver()

    query = DNSQuery(
        message_type="query",
        domain="unknown.xyz",
        record_type="A",
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

    assert calls == [("127.0.0.1", 5303)]
    assert response.status == ResponseStatus.ERROR
    assert response.error_code == ErrorCode.TLD_NOT_FOUND


def test_resolver_stops_if_tld_returns_error(monkeypatch) -> None:
    resolver = create_resolver()

    query = DNSQuery(
        message_type="query",
        domain="facebook.com",
        record_type="A",
    )

    calls = []

    def fake_query_server(query: DNSQuery, host: str, port: int) -> DNSResponse:
        calls.append((host, port))

        if port == 5303:
            return DNSResponse(
                message_type=MessageType.RESPONSE,
                status=ResponseStatus.OK,
                domain=".com",
                record_type=RecordType.TLD,
                value="127.0.0.1:5301",
            )

        if port == 5301:
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
        ("127.0.0.1", 5303),
        ("127.0.0.1", 5301),
    ]

    assert response.status == ResponseStatus.ERROR
    assert response.error_code == ErrorCode.AUTHORITATIVE_NOT_FOUND


def test_response_from_dict_builds_dns_response() -> None:
    resolver = create_resolver()

    response = resolver.response_from_dict(
        {
            "message_type": "response",
            "status": "ok",
            "domain": "maps.google.com",
            "record_type": "A",
            "value": "142.250.74.100",
            "ttl": 300,
        }
    )

    assert response.message_type == "response"
    assert response.status == "ok"
    assert response.domain == "maps.google.com"
    assert response.record_type == "A"
    assert response.value == "142.250.74.100"
    assert response.ttl == 300
