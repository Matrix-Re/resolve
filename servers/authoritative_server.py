import argparse
from pathlib import Path
from typing import Any

from core.server import BaseDNSServer
from core.message import DNSQuery, DNSResponse
from core.utils import extract_zone_domain
from core.config import load_json_file
from core.cli import add_common_server_args, add_zone_server_args


from core.constants import AUTHORITATIVE_DEFAULT_PORT
from core.enums import RecordType, ErrorCode, MessageType, ResponseStatus


class AuthoritativeServer(BaseDNSServer):
    """
    Authoritative DNS server.

    This server is responsible for resolving records contained in a DNS zone.
    """

    @property
    def server_name(self) -> str:
        return RecordType.AUTHORITATIVE

    def __init__(self, host: str, port: int, zone_path: str) -> None:
        super().__init__(host, port)
        self.zone_path = Path(zone_path)

    def load_zone(self, zone_name: str) -> dict[str, Any]:
        """
        Load a DNS zone from a JSON file.
        """
        zone = load_json_file(self.zone_path / zone_name)

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
                error_code=ErrorCode.NOT_FOUND,
                error_message=f"Domain not found in zone: {query.domain}",
            )

        record = domain_records.get(query.record_type)

        if record is None:
            return self.build_error_response(
                error_code=ErrorCode.RECORD_NOT_FOUND,
                error_message=(
                    f"Record type {query.record_type} not found "
                    f"for domain {query.domain}"
                ),
            )

        return DNSResponse(
            message_type=MessageType.RESPONSE,
            status=ResponseStatus.OK,
            domain=query.domain,
            record_type=query.record_type,
            value=record["value"],
            ttl=record["ttl"],
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Authoritative DNS server for ReSolve")

    add_common_server_args(parser, AUTHORITATIVE_DEFAULT_PORT)
    add_zone_server_args(parser)

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
