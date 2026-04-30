from core.message import DNSQuery

def test_dns_query_serialization():
    query = DNSQuery(message_type="query", domain="google.com", record_type="A")
    json_str = query.to_json()

    assert '"domain": "google.com"' in json_str
    assert '"record_type": "A"' in json_str