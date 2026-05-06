import argparse

from core.cli import (
    add_common_server_args,
    add_config_server_args,
    add_zone_server_args,
)
from core.constants import (
    DEFAULT_HOST,
    DEFAULT_ZONES_DIR,
    DEFAULT_TLD_CONFIG_PATH,
    RESOLVER_DEFAULT_PORT,
)


def test_add_common_server_args_with_default_values() -> None:
    parser = argparse.ArgumentParser()

    add_common_server_args(parser, default_port=RESOLVER_DEFAULT_PORT)

    args = parser.parse_args([])

    assert args.host == DEFAULT_HOST
    assert args.port == RESOLVER_DEFAULT_PORT


def test_add_common_server_args_with_custom_values() -> None:
    parser = argparse.ArgumentParser()

    add_common_server_args(parser, default_port=RESOLVER_DEFAULT_PORT)

    args = parser.parse_args(
        [
            "--host",
            "0.0.0.0",
            "--port",
            "5400",
        ]
    )

    assert args.host == "0.0.0.0"
    assert args.port == 5400


def test_add_config_server_args_with_default_value() -> None:
    parser = argparse.ArgumentParser()

    add_config_server_args(parser, path=DEFAULT_TLD_CONFIG_PATH)

    args = parser.parse_args([])

    assert args.config == DEFAULT_TLD_CONFIG_PATH


def test_add_config_server_args_with_custom_value() -> None:
    parser = argparse.ArgumentParser()

    add_config_server_args(parser, path=DEFAULT_TLD_CONFIG_PATH)

    args = parser.parse_args(
        [
            "--config",
            "custom/tld.json",
        ]
    )

    assert args.config == "custom/tld.json"


def test_add_zone_server_args_with_default_value() -> None:
    parser = argparse.ArgumentParser()

    add_zone_server_args(parser)

    args = parser.parse_args([])

    assert args.zones_path == DEFAULT_ZONES_DIR


def test_add_zone_server_args_with_custom_value() -> None:
    parser = argparse.ArgumentParser()

    add_zone_server_args(parser)

    args = parser.parse_args(
        [
            "--zones-path",
            "custom/zones",
        ]
    )

    assert args.zones_path == "custom/zones"
