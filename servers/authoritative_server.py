import argparse
from pathlib import Path
from typing import Any

from core.server import BaseDNSServer
from core.message import DNSQuery, DNSResponse
from core.utils import extract_zone_domain
from core.config import load_json_file


DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 5302
BUFFER_SIZE = 4096
DEFAULT_ZONE_PATH = "data/zones/"


class AuthoritativeServer(BaseDNSServer):
    """
    Authoritative DNS server.

    This server is responsible for resolving records contained in a DNS zone.
    """

    @property
    def server_name(self) -> str:
        return "AUTH"

    def __init__(self, host: str, port: int, zone_path: str) -> None:
        super().__init__(host, port)
        self.zone_path = Path(zone_path)

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

    def load_zone(self, zone_name: str) -> dict[str, Any]:
        """
        Load a DNS zone from a JSON file.
        """
        zone = load_json_file(f"{self.zone_path}/{zone_name}")

        if "domain" not in zone:
            raise ValueError("Invalid zone file: missing 'domain' field")

        if "records" not in zone:
            raise ValueError("Invalid zone file: missing 'records' field")

        return zone

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
