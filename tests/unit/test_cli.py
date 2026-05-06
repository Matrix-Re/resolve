import json
import socket

import pytest

from client.cli import build_query, display_response, main, send_query
from core.enums import MessageType, RecordType, ResponseStatus, ErrorCode
from core.constants import RESOLVER_DEFAULT_PORT, DEFAULT_HOST


def test_build_query() -> None:
    query = build_query("maps.google.com", RecordType.A)

    assert query == {
        "message_type": MessageType.QUERY,
        "domain": "maps.google.com",
        "record_type": RecordType.A,
    }


def test_display_response_success(capsys: pytest.CaptureFixture[str]) -> None:
    response = {
        "status": ResponseStatus.OK,
        "domain": "maps.google.com",
        "record_type": RecordType.A,
        "value": "142.250.74.100",
        "ttl": 300,
    }

    display_response(response)

    output = capsys.readouterr().out

    assert "DNS Response" in output
    assert "maps.google.com" in output
    assert RecordType.A in output
    assert "142.250.74.100" in output
    assert "300" in output


def test_display_response_error(capsys: pytest.CaptureFixture[str]) -> None:
    response = {
        "status": ResponseStatus.ERROR,
        "error_code": ErrorCode.NOT_FOUND,
        "error_message": "Domain not found",
    }

    display_response(response)

    output = capsys.readouterr().out

    assert "Error:" in output
    assert ErrorCode.NOT_FOUND.value in output
    assert "Domain not found" in output


class FakeSocketSuccess:
    def __init__(self, *args, **kwargs) -> None:
        self.timeout = None
        self.sent_payload = None
        self.sent_address = None
        self.closed = False

    def settimeout(self, timeout: int) -> None:
        self.timeout = timeout

    def sendto(self, payload: bytes, address: tuple[str, int]) -> None:
        self.sent_payload = payload
        self.sent_address = address

    def recvfrom(self, buffer_size: int) -> tuple[bytes, tuple[str, int]]:
        response = {
            "message_type": MessageType.RESPONSE,
            "status": ResponseStatus.OK,
            "domain": "maps.google.com",
            "record_type": RecordType.A,
            "value": "142.250.74.100",
            "ttl": 300,
        }

        return json.dumps(response).encode("utf-8"), (
            DEFAULT_HOST,
            RESOLVER_DEFAULT_PORT,
        )

    def close(self) -> None:
        self.closed = True


def test_send_query_success(monkeypatch: pytest.MonkeyPatch) -> None:
    fake_socket = FakeSocketSuccess()

    monkeypatch.setattr(socket, "socket", lambda *args, **kwargs: fake_socket)

    query = build_query("maps.google.com", RecordType.A)

    response = send_query(query, DEFAULT_HOST, RESOLVER_DEFAULT_PORT)

    assert response["status"] == ResponseStatus.OK
    assert response["domain"] == "maps.google.com"
    assert response["record_type"] == RecordType.A
    assert response["value"] == "142.250.74.100"
    assert response["ttl"] == 300

    assert fake_socket.sent_address == (DEFAULT_HOST, RESOLVER_DEFAULT_PORT)
    assert fake_socket.closed is True


class FakeSocketTimeout:
    def settimeout(self, timeout: int) -> None:
        pass

    def sendto(self, payload: bytes, address: tuple[str, int]) -> None:
        pass

    def recvfrom(self, buffer_size: int) -> tuple[bytes, tuple[str, int]]:
        raise socket.timeout

    def close(self) -> None:
        pass


def test_send_query_timeout(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(socket, "socket", lambda *args, **kwargs: FakeSocketTimeout())

    query = build_query("maps.google.com", RecordType.A)

    with pytest.raises(RuntimeError, match="Server timeout"):
        send_query(query, DEFAULT_HOST, RESOLVER_DEFAULT_PORT)


class FakeSocketInvalidJson:
    def settimeout(self, timeout: int) -> None:
        pass

    def sendto(self, payload: bytes, address: tuple[str, int]) -> None:
        pass

    def recvfrom(self, buffer_size: int) -> tuple[bytes, tuple[str, int]]:
        return b"{invalid-json", (DEFAULT_HOST, RESOLVER_DEFAULT_PORT)

    def close(self) -> None:
        pass


def test_send_query_invalid_json_response(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        socket,
        "socket",
        lambda *args, **kwargs: FakeSocketInvalidJson(),
    )

    query = build_query("maps.google.com", RecordType.A)

    with pytest.raises(RuntimeError, match="Invalid JSON response from server"):
        send_query(query, DEFAULT_HOST, RESOLVER_DEFAULT_PORT)


def test_main_success(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr(
        "sys.argv",
        [
            "cli.py",
            "maps.google.com",
            "--type",
            RecordType.A,
            "--host",
            DEFAULT_HOST,
            "--port",
            str(RESOLVER_DEFAULT_PORT),
        ],
    )

    monkeypatch.setattr(
        "client.cli.send_query",
        lambda query, host, port: {
            "status": ResponseStatus.OK,
            "domain": query["domain"],
            "record_type": query["record_type"],
            "value": "142.250.74.100",
            "ttl": 300,
        },
    )

    main()

    output = capsys.readouterr().out

    assert "maps.google.com" in output
    assert "142.250.74.100" in output


def test_main_runtime_error(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr(
        "sys.argv",
        [
            "cli.py",
            "maps.google.com",
            "--type",
            RecordType.A,
        ],
    )

    def fake_send_query(query, host, port):
        raise RuntimeError("Server timeout")

    monkeypatch.setattr("client.cli.send_query", fake_send_query)

    main()

    output = capsys.readouterr().out

    assert "Error: Server timeout" in output
