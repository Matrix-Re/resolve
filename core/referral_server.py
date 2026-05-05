from pathlib import Path
from typing import Callable

from core.config import load_json_file
from core.enums import ErrorCode, MessageType, ResponseStatus
from core.message import DNSQuery, DNSResponse
from core.server import BaseDNSServer


class ReferralDNSServer(BaseDNSServer):
    def __init__(
        self,
        host: str,
        port: int,
        config_path: str,
        key_extractor: Callable[[str], str],
        target_record_type: str,
        not_found_error_code: str,
        not_found_message: str,
        invalid_config_message: str,
    ) -> None:
        super().__init__(host, port)
        self.config_path = Path(config_path)
        self.key_extractor = key_extractor
        self.target_record_type = target_record_type
        self.not_found_error_code = not_found_error_code
        self.not_found_message = not_found_message
        self.invalid_config_message = invalid_config_message

    def resolve(self, query: DNSQuery) -> DNSResponse:
        config = load_json_file(self.config_path)

        lookup_key = self.key_extractor(query.domain)
        target_server = config.get(lookup_key)

        if target_server is None:
            return self.build_error_response(
                error_code=self.not_found_error_code,
                error_message=self.not_found_message.format(key=lookup_key),
            )

        host = target_server.get("host")
        port = target_server.get("port")

        if host is None or port is None:
            return self.build_error_response(
                error_code=ErrorCode.INVALID_CONFIG,
                error_message=self.invalid_config_message.format(key=lookup_key),
            )

        server_address = f"{host}:{port}"

        return DNSResponse(
            message_type=MessageType.RESPONSE,
            status=ResponseStatus.OK,
            domain=lookup_key,
            record_type=self.target_record_type,
            value=server_address,
            ttl=None,
        )
