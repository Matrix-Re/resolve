import argparse

from core.referral_server import ReferralDNSServer
from core.utils import extract_domain_suffix
from core.cli import add_common_server_args, add_config_server_args

from core.enums import RecordType, ErrorCode
from core.constants import ROOT_DEFAULT_PORT, DEFAULT_ROOT_CONFIG_PATH


class RootServer(ReferralDNSServer):
    """
    ROOT DNS server.

    This server is responsible for redirecting a domain to its TLD server.
    """

    @property
    def server_name(self) -> str:
        return RecordType.ROOT

    def __init__(self, host: str, port: int, config_path: str) -> None:
        super().__init__(
            host=host,
            port=port,
            config_path=config_path,
            key_extractor=extract_domain_suffix,
            target_record_type=RecordType.TLD,
            not_found_error_code=ErrorCode.TLD_NOT_FOUND,
            not_found_message="No TLD server found for suffix: {key}",
            invalid_config_message="Invalid TLD server config for suffix: {key}",
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Root DNS server for ReSolve")

    add_common_server_args(parser, ROOT_DEFAULT_PORT)
    add_config_server_args(parser, DEFAULT_ROOT_CONFIG_PATH)

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
