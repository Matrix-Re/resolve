import json
import socket
import threading
import time
from pathlib import Path

from core.enums import ResponseStatus, RecordType, MessageType

from resolver.recursive_resolver import RecursiveResolver
from servers.authoritative_server import AuthoritativeServer
from servers.root_server import RootServer
from servers.tld_server import TLDServer

from core.constants import BUFFER_SIZE, DEFAULT_HOST


def write_json(path: Path, content: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(content), encoding="utf-8")


def start_server(server) -> None:
    server.start()


def test_recursive_resolution_e2e(tmp_path: Path) -> None:
    root_config = tmp_path / "root.json"
    tld_config = tmp_path / "tld.json"
    zones_path = tmp_path / "zones"

    write_json(
        root_config,
        {
            ".com": {
                "host": DEFAULT_HOST,
                "port": 5401,
            }
        },
    )

    write_json(
        tld_config,
        {
            "google.com": {
                "host": DEFAULT_HOST,
                "port": 5402,
            }
        },
    )

    write_json(
        zones_path / "google.com.json",
        {
            "domain": "google.com",
            "records": {
                "maps.google.com": {
                    "A": {
                        "value": "142.250.74.100",
                        "ttl": 300,
                    }
                }
            },
        },
    )

    root_server = RootServer(
        host=DEFAULT_HOST,
        port=5403,
        config_path=str(root_config),
    )

    tld_server = TLDServer(
        host=DEFAULT_HOST,
        port=5401,
        config_path=str(tld_config),
    )

    authoritative_server = AuthoritativeServer(
        host=DEFAULT_HOST,
        port=5402,
        zone_path=str(zones_path),
    )

    resolver = RecursiveResolver(
        host=DEFAULT_HOST,
        port=5400,
        root_host=DEFAULT_HOST,
        root_port=5403,
        timeout=2,
    )

    for server in [root_server, tld_server, authoritative_server, resolver]:
        thread = threading.Thread(target=start_server, args=(server,), daemon=True)
        thread.start()

    time.sleep(0.5)

    query = {
        "message_type": MessageType.QUERY,
        "domain": "maps.google.com",
        "record_type": RecordType.A,
    }

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(3)

    try:
        sock.sendto(json.dumps(query).encode("utf-8"), (DEFAULT_HOST, 5400))
        data, _ = sock.recvfrom(BUFFER_SIZE)
        response = json.loads(data.decode("utf-8"))
    finally:
        sock.close()

    assert response["status"] == ResponseStatus.OK
    assert response["domain"] == "maps.google.com"
    assert response["record_type"] == RecordType.A
    assert response["value"] == "142.250.74.100"
    assert response["ttl"] == 300
