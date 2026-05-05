import argparse
from pathlib import Path

from core.server import BaseDNSServer
from core.message import DNSQuery, DNSResponse
from core.utils import extract_domain_suffix
from core.config import load_json_file

from core.enums import RecordType, ErrorCode, MessageType, ResponseStatus
from core.constants import DEFAULT_HOST, ROOT_DEFAULT_PORT, DEFAULT_ROOT_CONFIG_PATH


class RootServer(BaseDNSServer):
    """
    ROOT DNS server.

    This server is responsible for redirecting a domain to its TLD server.
    """

    @property
    def server_name(self) -> str:
        return RecordType.ROOT

    def __init__(self, host: str, port: int, config_path: str) -> None:
        super().__init__(host, port)
        self.config_path = Path(config_path)

    def resolve(self, query: DNSQuery) -> DNSResponse:
        """
        Resolve a query by returning the TLD server address.
        """
        config = load_json_file(self.config_path)

        suffix_domain = extract_domain_suffix(query.domain)
        tld_server = config.get(suffix_domain)

        if tld_server is None:
            return self.build_error_response(
                error_code=ErrorCode.TLD_NOT_FOUND,
                error_message=f"No TLD server found for domain: {suffix_domain}",
            )

        host = tld_server.get("host")
        port = tld_server.get("port")

        if host is None or port is None:
            return self.build_error_response(
                error_code="INVALID_TLD_CONFIG",
                error_message=f"Invalid tld server config for domain: {suffix_domain}",
            )

        tld_server_address = f"{host}:{port}"

        return DNSResponse(
            message_type=MessageType.RESPONSE,
            status=ResponseStatus.OK,
            domain=suffix_domain,
            record_type=RecordType.TLD,
            value=tld_server_address,
            ttl=None,
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Root DNS server for ReSolve")

    parser.add_argument(
        "--host",
        default=DEFAULT_HOST,
        help=f"Server host, default: {DEFAULT_HOST}",
    )

    parser.add_argument(
        "--port",
        type=int,
        default=ROOT_DEFAULT_PORT,
        help=f"Server port, default: {ROOT_DEFAULT_PORT}",
    )

    parser.add_argument(
        "--config",
        default=DEFAULT_ROOT_CONFIG_PATH,
        help=f"ROOT config file path, default: {DEFAULT_ROOT_CONFIG_PATH}",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    server = RootServer(
        host=args.host,
        port=args.port,
        config_path=args.config,
    )

    server.start()


if __name__ == "__main__":
    main()
