import argparse
from pathlib import Path

from core.server import BaseDNSServer
from core.message import DNSQuery, DNSResponse
from core.utils import extract_zone_domain
from core.config import load_json_file

from core.enums import RecordType, ErrorCode, MessageType, ResponseStatus
from core.constants import DEFAULT_HOST, TLD_DEFAULT_PORT, DEFAULT_TLD_CONFIG_PATH


class TLDServer(BaseDNSServer):
    """
    TLD DNS server.

    This server is responsible for redirecting a domain to its authoritative server.
    """

    @property
    def server_name(self) -> str:
        return RecordType.TLD

    def __init__(self, host: str, port: int, config_path: str) -> None:
        super().__init__(host, port)
        self.config_path = Path(config_path)

    def resolve(self, query: DNSQuery) -> DNSResponse:
        """
        Resolve a query by returning the authoritative server address.
        """
        config = load_json_file(self.config_path)

        zone_domain = extract_zone_domain(query.domain)
        authoritative_server = config.get(zone_domain)

        if authoritative_server is None:
            return self.build_error_response(
                error_code=ErrorCode.AUTHORITATIVE_NOT_FOUND,
                error_message=f"No authoritative server found for domain: {zone_domain}",
            )

        host = authoritative_server.get("host")
        port = authoritative_server.get("port")

        if host is None or port is None:
            return self.build_error_response(
                error_code="INVALID_TLD_CONFIG",
                error_message=f"Invalid authoritative server config for domain: {zone_domain}",
            )

        authoritative_server_address = f"{host}:{port}"

        return DNSResponse(
            message_type=MessageType.RESPONSE,
            status=ResponseStatus.OK,
            domain=zone_domain,
            record_type=RecordType.AUTHORITATIVE,
            value=authoritative_server_address,
            ttl=None,
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="TLD DNS server for ReSolve")

    parser.add_argument(
        "--host",
        default=DEFAULT_HOST,
        help=f"Server host, default: {DEFAULT_HOST}",
    )

    parser.add_argument(
        "--port",
        type=int,
        default=TLD_DEFAULT_PORT,
        help=f"Server port, default: {TLD_DEFAULT_PORT}",
    )

    parser.add_argument(
        "--config",
        default=DEFAULT_TLD_CONFIG_PATH,
        help=f"TLD config file path, default: {DEFAULT_TLD_CONFIG_PATH}",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    server = TLDServer(
        host=args.host,
        port=args.port,
        config_path=args.config,
    )

    server.start()


if __name__ == "__main__":
    main()
