import json
import socket

from core.message import DNSQuery, DNSResponse


class DNSServer:
    def __init__(self, host: str = "127.0.0.1", port: int = 5300) -> None:
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def start(self) -> None:
        self.socket.bind((self.host, self.port))
        print(f"DNS server listening on {self.host}:{self.port}")

        while True:
            data, addr = self.socket.recvfrom(4096)
            response = self.handle_request(data)
            self.socket.sendto(response.encode("utf-8"), addr)

    def handle_request(self, data: bytes) -> str:
        try:
            payload = data.decode("utf-8")
            query = DNSQuery.from_json(payload)

            return self.handle_query(query).to_json()

        except json.JSONDecodeError:
            return DNSResponse(
                message_type="response",
                status="error",
                error_code="INVALID_JSON",
                error_message="Invalid JSON format",
            ).to_json()

        except KeyError as exc:
            return DNSResponse(
                message_type="response",
                status="error",
                error_code="INVALID_REQUEST",
                error_message=f"Missing field: {exc.args[0]}",
            ).to_json()

    def handle_query(self, query: DNSQuery) -> DNSResponse:
        """
        Logique métier du serveur DNS.
        Pour l'instant on mock les réponse en utilisant une base de données fictive.
        """
        fake_db = {
            ("google.com", "A"): ("142.250.74.68", 300),
            ("google.com", "AAAA"): ("2001:4860:4860::8888", 300),
        }

        result = fake_db.get((query.domain, query.record_type))

        if result is None:
            return DNSResponse(
                message_type="response",
                status="error",
                error_code="NOT_FOUND",
                error_message="Domain not found",
            )

        value, ttl = result

        return DNSResponse(
            message_type="response",
            status="ok",
            domain=query.domain,
            record_type=query.record_type,
            value=value,
            ttl=ttl,
        )


def main() -> None:
    server = DNSServer()
    server.start()


if __name__ == "__main__":
    main()