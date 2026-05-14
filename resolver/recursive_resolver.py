import argparse
import json
import socket
import threading
import time

from core.cli import add_common_server_args
from core.constants import (
    BUFFER_SIZE,
    DEFAULT_HOST,
    DEFAULT_TIMEOUT,
    RESOLVER_DEFAULT_PORT,
    ROOT_DEFAULT_PORT,
)
from core.enums import ErrorCode, MessageType, ResponseStatus
from core.message import DNSQuery, DNSResponse
from core.network import parse_server_address
from core.server import BaseDNSServer
from core.cache import DNSCache


class RecursiveResolver(BaseDNSServer):
    """
    Recursive DNS resolver without cache.

    This resolver receives a DNS query from a client and performs the full
    resolution chain:
    Resolver -> Root -> TLD -> Authoritative server
    """

    @property
    def server_name(self) -> str:
        return "RESOLVER"

    def __init__(
        self,
        host: str,
        port: int,
        root_host: str,
        root_port: int,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> None:
        super().__init__(host, port)
        self.root_host = root_host
        self.root_port = root_port
        self.timeout = timeout
        self.cache = DNSCache()

    def resolve(self, query: DNSQuery) -> DNSResponse:
        """
        Resolve a DNS query by contacting Root, TLD and Authoritative servers.
        """
        cached_response = self.cache.get(query)

        if cached_response is not None:
            return cached_response

        root_response = self.query_server(
            query=query,
            host=self.root_host,
            port=self.root_port,
        )

        if root_response.status != ResponseStatus.OK:
            return root_response

        tld_host, tld_port = self.extract_next_server(root_response)

        tld_response = self.query_server(
            query=query,
            host=tld_host,
            port=tld_port,
        )

        if tld_response.status != ResponseStatus.OK:
            return tld_response

        auth_host, auth_port = self.extract_next_server(tld_response)

        authoritative_response = self.query_server(
            query=query,
            host=auth_host,
            port=auth_port,
        )

        if authoritative_response.status == ResponseStatus.OK:
            self.cache.set(query, authoritative_response)

        return authoritative_response

    def query_server(self, query: DNSQuery, host: str, port: int) -> DNSResponse:
        """
        Send a DNSQuery to another DNS server and return its DNSResponse.
        """
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(self.timeout)

        try:
            sock.sendto(query.to_json().encode("utf-8"), (host, port))

            data, _ = sock.recvfrom(BUFFER_SIZE)
            payload = json.loads(data.decode("utf-8"))

            return self.response_from_dict(payload)

        except socket.timeout:
            return self.build_error_response(
                error_code=ErrorCode.SERVER_ERROR,
                error_message=f"Timeout while contacting server {host}:{port}",
            )

        except json.JSONDecodeError:
            return self.build_error_response(
                error_code=ErrorCode.INVALID_JSON,
                error_message=f"Invalid JSON response from server {host}:{port}",
            )

        finally:
            sock.close()

    def extract_next_server(self, response: DNSResponse) -> tuple[str, int]:
        """
        Extract the next server address from a DNSResponse value.
        """
        if response.value is None:
            raise ValueError("Missing server address in DNS response")

        return parse_server_address(response.value)

    def response_from_dict(self, data: dict) -> DNSResponse:
        """
        Convert a response dictionary into a DNSResponse object.
        """
        return DNSResponse(
            message_type=data.get("message_type", MessageType.RESPONSE),
            status=data.get("status", ResponseStatus.ERROR),
            domain=data.get("domain"),
            record_type=data.get("record_type"),
            value=data.get("value"),
            ttl=data.get("ttl"),
            error_code=data.get("error_code"),
            error_message=data.get("error_message"),
        )

    def start_cache_display(self, refresh_interval: int = 1) -> None:
        """
        Start a background thread that continuously displays the cache content.
        """

        def display_loop() -> None:
            while True:
                self.cache.display()
                time.sleep(refresh_interval)

        thread = threading.Thread(target=display_loop, daemon=True)
        thread.start()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Recursive DNS resolver for ReSolve")

    add_common_server_args(parser, RESOLVER_DEFAULT_PORT)

    parser.add_argument(
        "--root-host",
        default=DEFAULT_HOST,
        help=f"Root server host, default: {DEFAULT_HOST}",
    )

    parser.add_argument(
        "--root-port",
        type=int,
        default=ROOT_DEFAULT_PORT,
        help=f"Root server port, default: {ROOT_DEFAULT_PORT}",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    resolver = RecursiveResolver(
        host=args.host,
        port=args.port,
        root_host=args.root_host,
        root_port=args.root_port,
    )

    resolver.start_cache_display()
    resolver.start()


if __name__ == "__main__":
    main()
