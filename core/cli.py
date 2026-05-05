import argparse

from core.constants import DEFAULT_HOST, DEFAULT_ZONES_DIR


def add_common_server_args(parser: argparse.ArgumentParser, default_port: int) -> None:
    parser.add_argument(
        "--host",
        default=DEFAULT_HOST,
        help=f"Server host, default: {DEFAULT_HOST}",
    )

    parser.add_argument(
        "--port",
        type=int,
        default=default_port,
        help=f"Server port, default: {default_port}",
    )


def add_config_server_args(parser: argparse.ArgumentParser, path: str) -> None:
    parser.add_argument(
        "--config",
        default=path,
        help=f"Config file path, default: {path}",
    )


def add_zone_server_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--zones-path",
        default=DEFAULT_ZONES_DIR,
        help=f"Path to the DNS zones directory, default: {DEFAULT_ZONES_DIR}",
    )
