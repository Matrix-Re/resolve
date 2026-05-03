from dataclasses import dataclass, asdict
import json


@dataclass
class DNSQuery:
    message_type: str
    domain: str
    record_type: str

    def __post_init__(self) -> None:
        self.message_type = self.message_type.strip().lower()
        self.domain = self.domain.strip().lower().removesuffix(".")
        self.record_type = self.record_type.strip().upper()

    def to_json(self) -> str:
        return json.dumps(asdict(self))

    @staticmethod
    def from_json(payload: str) -> "DNSQuery":
        data = json.loads(payload)
        return DNSQuery(
            message_type=data["message_type"],
            domain=data["domain"],
            record_type=data["record_type"],
        )


@dataclass
class DNSResponse:
    message_type: str
    status: str
    domain: str | None = None
    record_type: str | None = None
    value: str | None = None
    ttl: int | None = None
    error_code: str | None = None
    error_message: str | None = None

    def to_json(self) -> str:
        return json.dumps(asdict(self))
