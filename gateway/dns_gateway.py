# gateway/dns_gateway.py

import argparse
import json
import socket

from dnslib import A, AAAA, DNSHeader, DNSRecord, QTYPE, RR

from core.constants import BUFFER_SIZE, DEFAULT_HOST
from core.enums import MessageType, RecordType, ResponseStatus


class DNSGateway:
    """
    Standard DNS gateway.

    This component receives standard DNS requests and translates them into
    the internal JSON DNS protocol used by ReSolve.
    """

    def __init__(
        self,
        host: str,
        port: int,
        resolver_host: str,
        resolver_port: int,
        timeout: int = 3,
    ) -> None:
        self.host = host
        self.port = port
        self.resolver_host = resolver_host
        self.resolver_port = resolver_port
        self.timeout = timeout

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def start(self) -> None:
        self.socket.bind((self.host, self.port))
        print(f"[DNS_GATEWAY] Listening on {self.host}:{self.port}")
        print(
            f"[DNS_GATEWAY] Forwarding to resolver {self.resolver_host}:{self.resolver_port}"
        )

        while True:
            data, address = self.socket.recvfrom(BUFFER_SIZE)
            response = self.handle_dns_request(data)
            self.socket.sendto(response, address)

    def handle_dns_request(self, data: bytes) -> bytes:
        try:
            dns_request = DNSRecord.parse(data)

            question = dns_request.q
            domain = str(question.qname).rstrip(".")
            record_type = QTYPE[question.qtype]

            print(f"[DNS_GATEWAY] Query received: {domain} {record_type}")

            if record_type not in {RecordType.A, RecordType.AAAA}:
                return self.build_error_response(dns_request, rcode=4)

            resolver_response = self.query_resolver(domain, record_type)

            return self.build_dns_response(dns_request, resolver_response)

        except Exception as error:
            print(f"[DNS_GATEWAY] Error: {error}")

            try:
                dns_request = DNSRecord.parse(data)
                return self.build_error_response(dns_request, rcode=2)
            except Exception:
                return DNSRecord(
                    DNSHeader(qr=1, ra=1, rcode=2),
                ).pack()

    def query_resolver(self, domain: str, record_type: str) -> dict:
        """
        Forward a standard DNS request to the internal ReSolve resolver.
        """
        query = {
            "message_type": MessageType.QUERY,
            "domain": domain,
            "record_type": record_type,
        }

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(self.timeout)

        try:
            sock.sendto(
                json.dumps(query).encode("utf-8"),
                (self.resolver_host, self.resolver_port),
            )

            data, _ = sock.recvfrom(BUFFER_SIZE)
            return json.loads(data.decode("utf-8"))

        finally:
            sock.close()

    def build_dns_response(
        self, dns_request: DNSRecord, resolver_response: dict
    ) -> bytes:
        reply = dns_request.reply()

        if resolver_response.get("status") != ResponseStatus.OK:
            reply.header.rcode = 3
            return reply.pack()

        domain = resolver_response.get("domain")
        record_type = resolver_response.get("record_type")
        value = resolver_response.get("value")
        ttl = resolver_response.get("ttl") or 300

        if not domain or not record_type or not value:
            reply.header.rcode = 2
            return reply.pack()

        if record_type == RecordType.A:
            rdata = A(value)
        elif record_type == RecordType.AAAA:
            rdata = AAAA(value)
        else:
            reply.header.rcode = 4
            return reply.pack()

        reply.add_answer(
            RR(
                rname=dns_request.q.qname,
                rtype=QTYPE.reverse[record_type],
                rclass=1,
                ttl=int(ttl),
                rdata=rdata,
            )
        )

        return reply.pack()

    def build_error_response(self, dns_request: DNSRecord, rcode: int) -> bytes:
        reply = dns_request.reply()
        reply.header.rcode = rcode
        return reply.pack()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Standard DNS gateway for ReSolve")

    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Gateway listening host, default: 0.0.0.0",
    )

    parser.add_argument(
        "--port",
        type=int,
        default=53,
        help="Gateway listening port, default: 53",
    )

    parser.add_argument(
        "--resolver-host",
        default=DEFAULT_HOST,
        help=f"Internal resolver host, default: {DEFAULT_HOST}",
    )

    parser.add_argument(
        "--resolver-port",
        type=int,
        default=5300,
        help="Internal resolver port, default: 5300",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    gateway = DNSGateway(
        host=args.host,
        port=args.port,
        resolver_host=args.resolver_host,
        resolver_port=args.resolver_port,
    )

    gateway.start()


if __name__ == "__main__":
    main()
