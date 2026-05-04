import json
import socket
from abc import ABC, abstractmethod

from core.message import DNSQuery, DNSResponse


BUFFER_SIZE = 4096


class BaseDNSServer(ABC):
    def __init__(self, host: str, port: int) -> None:
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def start(self) -> None:
        self.socket.bind((self.host, self.port))
        print(f"[{self.server_name}] Server started on {self.host}:{self.port}")

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
                "INVALID_JSON",
                "Request payload is not valid JSON",
            )

        except KeyError as error:
            return self.build_error_response(
                "INVALID_REQUEST",
                f"Missing field: {error.args[0]}",
            )

        except UnicodeDecodeError:
            return self.build_error_response(
                "INVALID_ENCODING",
                "Request payload must be UTF-8 encoded",
            )

        except FileNotFoundError as error:
            return self.build_error_response(
                "CONFIG_NOT_FOUND",
                str(error),
            )

        except ValueError as error:
            return self.build_error_response(
                "INVALID_CONFIG",
                str(error),
            )

        except Exception as error:
            return self.build_error_response(
                "SERVER_ERROR",
                str(error),
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

    @property
    @abstractmethod
    def server_name(self) -> str:
        pass

    @abstractmethod
    def resolve(self, query: DNSQuery) -> DNSResponse:
        pass
