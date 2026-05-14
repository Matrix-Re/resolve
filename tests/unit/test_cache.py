import time

from core.cache import DNSCache
from core.enums import MessageType, RecordType, ResponseStatus
from core.message import DNSQuery, DNSResponse


def create_query() -> DNSQuery:
    return DNSQuery(
        message_type=MessageType.QUERY,
        domain="maps.google.com",
        record_type=RecordType.A,
    )


def create_response(ttl: int | None = 300) -> DNSResponse:
    return DNSResponse(
        message_type=MessageType.RESPONSE,
        status=ResponseStatus.OK,
        domain="maps.google.com",
        record_type=RecordType.A,
        value="142.250.74.100",
        ttl=ttl,
    )


def test_cache_returns_none_on_miss() -> None:
    cache = DNSCache()
    query = create_query()

    assert cache.get(query) is None


def test_cache_returns_response_on_hit() -> None:
    cache = DNSCache()
    query = create_query()
    response = create_response(ttl=300)

    cache.set(query, response)

    cached_response = cache.get(query)

    assert cached_response is response
    assert cached_response.value == "142.250.74.100"


def test_cache_expires_response_after_ttl() -> None:
    cache = DNSCache()
    query = create_query()
    response = create_response(ttl=1)

    cache.set(query, response)

    assert cache.get(query) is not None

    time.sleep(1.1)

    assert cache.get(query) is None


def test_cache_does_not_store_response_without_ttl() -> None:
    cache = DNSCache()
    query = create_query()
    response = create_response(ttl=None)

    cache.set(query, response)

    assert cache.get(query) is None


def test_cache_does_not_store_response_with_zero_ttl() -> None:
    cache = DNSCache()
    query = create_query()
    response = create_response(ttl=0)

    cache.set(query, response)

    assert cache.get(query) is None


def test_cache_uses_domain_and_record_type_as_key() -> None:
    cache = DNSCache()

    query_a = DNSQuery(
        message_type=MessageType.QUERY,
        domain="maps.google.com",
        record_type=RecordType.A,
    )

    query_aaaa = DNSQuery(
        message_type=MessageType.QUERY,
        domain="maps.google.com",
        record_type=RecordType.AAAA,
    )

    response_a = create_response(ttl=300)

    cache.set(query_a, response_a)

    assert cache.get(query_a) is response_a
    assert cache.get(query_aaaa) is None


def test_cache_clear_removes_entries() -> None:
    cache = DNSCache()
    query = create_query()
    response = create_response(ttl=300)

    cache.set(query, response)

    assert cache.size() == 1

    cache.clear()

    assert cache.size() == 0
    assert cache.get(query) is None
