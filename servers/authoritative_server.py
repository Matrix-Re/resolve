import argparse
import json
import socket
from pathlib import Path
from typing import Any

from core.message import DNSQuery, DNSResponse
from core.utils import extract_zone_domain


DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 5302
BUFFER_SIZE = 4096
DEFAULT_ZONE_PATH = "data/zones/"


class AuthoritativeServer:
    """
    Authoritative DNS server.

    This server is responsible for resolving records contained in a DNS zone.
    """

    def __init__(self, host: str, port: int, zone_path: str) -> None:
        self.host = host
        self.port = port
        self.zone_path = Path(zone_path)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def load_zone(self, zone_name: str) -> dict[str, Any]:
        """
        Load a DNS zone from a JSON file.
        """
        zone_file = self.zone_path / f"{zone_name}.json"
        if not zone_file.exists():
            raise FileNotFoundError(f"Zone file not found: {zone_file}")

        with zone_file.open("r", encoding="utf-8") as file:
            zone = json.load(file)

        if "domain" not in zone:
            raise ValueError("Invalid zone file: missing 'domain' field")

        if "records" not in zone:
            raise ValueError("Invalid zone file: missing 'records' field")

        return zone

    def start(self) -> None:
        """
        Start the UDP authoritative server.
        """
        self.socket.bind((self.host, self.port))

        print(f"[AUTH] Authoritative server started on {self.host}:{self.port} ")

        while True:
            data, address = self.socket.recvfrom(BUFFER_SIZE)
            response = self.handle_request(data)
            self.socket.sendto(response.to_json().encode("utf-8"), address)

    def handle_request(self, data: bytes) -> DNSResponse:
        """
        Decode and process an incoming request.
        """
        try:
            payload = data.decode("utf-8")
            query = DNSQuery.from_json(payload)

            return self.resolve(query)

        except json.JSONDecodeError:
            return self.build_error_response(
                error_code="INVALID_JSON",
                error_message="Request payload is not valid JSON",
            )

        except KeyError as error:
            return self.build_error_response(
                error_code="INVALID_REQUEST",
                error_message=f"Missing field: {error.args[0]}",
            )

        except UnicodeDecodeError:
            return self.build_error_response(
                error_code="INVALID_ENCODING",
                error_message="Request payload must be UTF-8 encoded",
            )

        except FileNotFoundError as error:
            return self.build_error_response(
                error_code="ZONE_NOT_FOUND",
                error_message=str(error),
            )

        except Exception as error:
            return self.build_error_response(
                error_code="SERVER_ERROR",
                error_message=str(error),
            )

    def resolve(self, query: DNSQuery) -> DNSResponse:
        """
        Resolve a DNS query using the zone.
        """
        load_zone_response = self.load_zone(extract_zone_domain(query.domain))

        records = load_zone_response["records"]

        domain_records = records.get(query.domain)

        if domain_records is None:
            return self.build_error_response(
                error_code="NOT_FOUND",
                error_message=f"Domain not found in zone: {query.domain}",
            )

        record = domain_records.get(query.record_type)

        if record is None:
            return self.build_error_response(
                error_code="RECORD_NOT_FOUND",
                error_message=(
                    f"Record type {query.record_type} not found "
                    f"for domain {query.domain}"
                ),
            )

        return DNSResponse(
            message_type="response",
            status="ok",
            domain=query.domain,
            record_type=query.record_type,
            value=record["value"],
            ttl=record["ttl"],
        )

    def build_error_response(self, error_code: str, error_message: str) -> DNSResponse:
        """
        Build a standard DNS error response.
        """
        return DNSResponse(
            message_type="response",
            status="error",
            error_code=error_code,
            error_message=error_message,
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Authoritative DNS server for ReSolve")

    parser.add_argument(
        "--host",
        default=DEFAULT_HOST,
        help=f"Server host, default: {DEFAULT_HOST}",
    )

    parser.add_argument(
        "--port",
        type=int,
        default=DEFAULT_PORT,
        help=f"Server port, default: {DEFAULT_PORT}",
    )

    parser.add_argument(
        "--zones-path",
        default=DEFAULT_ZONE_PATH,
        help=f"Path to the DNS zones directory, default: {DEFAULT_ZONE_PATH}",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    server = AuthoritativeServer(
        host=args.host,
        port=args.port,
        zone_path=args.zones_path,
    )

    server.start()


if __name__ == "__main__":
    main()
