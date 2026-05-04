import argparse
import json
import socket
from pathlib import Path
from typing import Any

from core.message import DNSQuery, DNSResponse
from core.utils import extract_zone_domain


DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 5301
BUFFER_SIZE = 4096
DEFAULT_TLD_CONFIG_PATH = "data/tld.json"


class TLDServer:
    """
    TLD DNS server.

    This server is responsible for redirecting a domain to its authoritative server.
    Example:
    - maps.google.com -> google.com -> 127.0.0.1:5302
    """

    def __init__(self, host: str, port: int, config_path: str) -> None:
        self.host = host
        self.port = port
        self.config_path = Path(config_path)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def load_config(self) -> dict[str, Any]:
        """
        Load the TLD configuration file.
        """
        if not self.config_path.exists():
            raise FileNotFoundError(f"TLD config file not found: {self.config_path}")

        with self.config_path.open("r", encoding="utf-8") as file:
            config = json.load(file)

        if not isinstance(config, dict):
            raise ValueError("Invalid TLD config: root element must be an object")

        return config

    def start(self) -> None:
        """
        Start the UDP TLD server.
        """
        self.socket.bind((self.host, self.port))

        print(f"[TLD] TLD server started on {self.host}:{self.port}")

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
                error_code="TLD_CONFIG_NOT_FOUND",
                error_message=str(error),
            )

        except ValueError as error:
            return self.build_error_response(
                error_code="INVALID_TLD_CONFIG",
                error_message=str(error),
            )

        except Exception as error:
            return self.build_error_response(
                error_code="SERVER_ERROR",
                error_message=str(error),
            )

    def resolve(self, query: DNSQuery) -> DNSResponse:
        """
        Resolve a query by returning the authoritative server address.
        """
        config = self.load_config()

        zone_domain = extract_zone_domain(query.domain)
        authoritative_server = config.get(zone_domain)

        if authoritative_server is None:
            return self.build_error_response(
                error_code="AUTHORITATIVE_NOT_FOUND",
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
            message_type="response",
            status="ok",
            domain=zone_domain,
            record_type="AUTHORITATIVE",
            value=authoritative_server_address,
            ttl=None,
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
    parser = argparse.ArgumentParser(description="TLD DNS server for ReSolve")

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
