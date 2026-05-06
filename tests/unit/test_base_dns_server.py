import json

from core.enums import ErrorCode, MessageType, ResponseStatus, RecordType
from core.message import DNSQuery, DNSResponse
from core.server import BaseDNSServer

from core.constants import DEFAULT_HOST


class DummyDNSServer(BaseDNSServer):
    def __init__(self, exception_to_raise: Exception | None = None) -> None:
        super().__init__(host=DEFAULT_HOST, port=9999)
        self.exception_to_raise = exception_to_raise

    @property
    def server_name(self) -> str:
        return "DUMMY"

    def resolve(self, query: DNSQuery) -> DNSResponse:
        if self.exception_to_raise is not None:
            raise self.exception_to_raise

        return DNSResponse(
            message_type=MessageType.RESPONSE,
            status=ResponseStatus.OK,
            domain=query.domain,
            record_type=query.record_type,
            value=DEFAULT_HOST,
            ttl=300,
        )


def build_valid_query_payload() -> bytes:
    return json.dumps(
        {
            "message_type": MessageType.QUERY,
            "domain": "google.com",
            "record_type": RecordType.A,
        }
    ).encode("utf-8")


def test_handle_request_success() -> None:
    server = DummyDNSServer()

    response = server.handle_request(build_valid_query_payload())

    assert response.status == ResponseStatus.OK
    assert response.domain == "google.com"
    assert response.record_type == RecordType.A
    assert response.value == DEFAULT_HOST
    assert response.ttl == 300


def test_handle_request_invalid_json_returns_error() -> None:
    server = DummyDNSServer()

    response = server.handle_request(b"{invalid-json")

    assert response.status == ResponseStatus.ERROR
    assert response.error_code == ErrorCode.INVALID_JSON
    assert response.error_message == "Request payload is not valid JSON"


def test_handle_request_missing_field_returns_error() -> None:
    server = DummyDNSServer()

    payload = json.dumps(
        {
            "message_type": MessageType.QUERY,
            "domain": "google.com",
        }
    ).encode("utf-8")

    response = server.handle_request(payload)

    assert response.status == ResponseStatus.ERROR
    assert response.error_code == ErrorCode.INVALID_REQUEST
    assert "Missing field" in response.error_message


def test_handle_request_invalid_encoding_returns_error() -> None:
    server = DummyDNSServer()

    response = server.handle_request(b"\xff\xfe\xfa")

    assert response.status == ResponseStatus.ERROR
    assert response.error_code == ErrorCode.INVALID_ENCODING
    assert response.error_message == "Request payload must be UTF-8 encoded"


def test_handle_request_file_not_found_returns_config_not_found() -> None:
    server = DummyDNSServer(
        exception_to_raise=FileNotFoundError("Config file not found")
    )

    response = server.handle_request(build_valid_query_payload())

    assert response.status == ResponseStatus.ERROR
    assert response.error_code == ErrorCode.CONFIG_NOT_FOUND
    assert "Config file not found" in response.error_message


def test_handle_request_value_error_returns_invalid_config() -> None:
    server = DummyDNSServer(exception_to_raise=ValueError("Invalid config"))

    response = server.handle_request(build_valid_query_payload())

    assert response.status == ResponseStatus.ERROR
    assert response.error_code == ErrorCode.INVALID_CONFIG
    assert "Invalid config" in response.error_message


def test_handle_request_unknown_exception_returns_server_error() -> None:
    server = DummyDNSServer(exception_to_raise=RuntimeError("Unexpected failure"))

    response = server.handle_request(build_valid_query_payload())

    assert response.status == ResponseStatus.ERROR
    assert response.error_code == ErrorCode.SERVER_ERROR
    assert "Unexpected failure" in response.error_message


def test_build_error_response() -> None:
    server = DummyDNSServer()

    response = server.build_error_response(
        error_code=ErrorCode.SERVER_ERROR,
        error_message="Something went wrong",
    )

    assert response.message_type == MessageType.RESPONSE
    assert response.status == ResponseStatus.ERROR
    assert response.error_code == ErrorCode.SERVER_ERROR
    assert response.error_message == "Something went wrong"
