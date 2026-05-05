import argparse

from core.referral_server import ReferralDNSServer
from core.utils import extract_zone_domain
from core.cli import add_common_server_args, add_config_server_args

from core.enums import RecordType, ErrorCode
from core.constants import TLD_DEFAULT_PORT, DEFAULT_TLD_CONFIG_PATH


class TLDServer(ReferralDNSServer):
    """
    TLD DNS server.

    This server is responsible for redirecting a domain to its authoritative server.
    """

    @property
    def server_name(self) -> str:
        return RecordType.TLD

    def __init__(self, host: str, port: int, config_path: str) -> None:
        super().__init__(
            host=host,
            port=port,
            config_path=config_path,
            key_extractor=extract_zone_domain,
            target_record_type=RecordType.AUTHORITATIVE,
            not_found_error_code=ErrorCode.AUTHORITATIVE_NOT_FOUND,
            not_found_message="No authoritative server found for domain: {key}",
            invalid_config_message="Invalid authoritative server config for domain: {key}",
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="TLD DNS server for ReSolve")

    add_common_server_args(parser, TLD_DEFAULT_PORT)
    add_config_server_args(parser, DEFAULT_TLD_CONFIG_PATH)

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
