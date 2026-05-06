from core.message import DNSQuery

from core.enums import MessageType, RecordType


def test_dns_query_serialization():
    query = DNSQuery(
        message_type=MessageType.QUERY, domain="google.com", record_type=RecordType.A
    )
    json_str = query.to_json()

    assert '"domain": "google.com"' in json_str
    assert '"record_type": "A"' in json_str
