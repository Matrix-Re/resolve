import socket
import json
import threading
import time

from servers.server import DNSServer


def start_server():
    server = DNSServer(host="127.0.0.1", port=5300)
    server.start()


def test_server_response():
    # Lancer le serveur en arrière-plan
    thread = threading.Thread(target=start_server, daemon=True)
    thread.start()

    # Laisser le temps au serveur de démarrer
    time.sleep(0.5)

    query = {"message_type": "query", "domain": "google.com", "record_type": "A"}

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(2)

    sock.sendto(json.dumps(query).encode(), ("127.0.0.1", 5300))

    data, _ = sock.recvfrom(4096)
    response = json.loads(data.decode())

    assert response["status"] == "ok"
    assert response["domain"] == "google.com"

    sock.close()
