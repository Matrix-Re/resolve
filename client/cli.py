import argparse
import json
import socket
from typing import Dict, Any


DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 5300
TIMEOUT = 3


def build_query(domain: str, record_type: str) -> Dict[str, Any]:
    return {
        "message_type": "query",
        "domain": domain,
        "record_type": record_type,
    }


def send_query(query: Dict[str, Any], host: str, port: int) -> Dict[str, Any]:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(TIMEOUT)

    try:
        payload = json.dumps(query).encode("utf-8")
        sock.sendto(payload, (host, port))

        data, _ = sock.recvfrom(4096)
        return json.loads(data.decode("utf-8"))

    except socket.timeout:
        raise RuntimeError("Server timeout")

    except json.JSONDecodeError:
        raise RuntimeError("Invalid JSON response from server")

    finally:
        sock.close()


def display_response(response: Dict[str, Any]) -> None:
    print("\n=== DNS Response ===")

    status = response.get("status")

    if status == "ok":
        print(f"Domain       : {response.get('domain')}")
        print(f"Record type  : {response.get('record_type')}")
        print(f"Value        : {response.get('value')}")
        print(f"TTL          : {response.get('ttl')}")
    else:
        print("Error:")
        print(f"Code         : {response.get('error_code')}")
        print(f"Message      : {response.get('error_message')}")

    print("====================\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="DNS CLI Client (ReSolve)")

    parser.add_argument(
        "domain",
        help="Domain name to resolve (ex: google.com)",
    )

    parser.add_argument(
        "--type",
        dest="record_type",
        default="A",
        choices=["A", "AAAA"],
        help="DNS record type (default: A)",
    )

    parser.add_argument(
        "--host",
        default=DEFAULT_HOST,
        help=f"DNS server host (default: {DEFAULT_HOST})",
    )

    parser.add_argument(
        "--port",
        type=int,
        default=DEFAULT_PORT,
        help=f"DNS server port (default: {DEFAULT_PORT})",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    query = build_query(args.domain, args.record_type)

    try:
        response = send_query(query, args.host, args.port)
        display_response(response)

    except RuntimeError as e:
        print(f"\nError: {e}\n")


if __name__ == "__main__":
    main()
