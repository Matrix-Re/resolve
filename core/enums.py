from enum import StrEnum


class MessageType(StrEnum):
    QUERY = "query"
    RESPONSE = "response"


class ResponseStatus(StrEnum):
    OK = "ok"
    ERROR = "error"


class RecordType(StrEnum):
    A = "A"
    AAAA = "AAAA"
    TLD = "TLD"
    AUTHORITATIVE = "AUTHORITATIVE"


class ErrorCode(StrEnum):
    INVALID_JSON = "INVALID_JSON"
    INVALID_REQUEST = "INVALID_REQUEST"
    INVALID_ENCODING = "INVALID_ENCODING"
    SERVER_ERROR = "SERVER_ERROR"
    NOT_FOUND = "NOT_FOUND"
    RECORD_NOT_FOUND = "RECORD_NOT_FOUND"
    ZONE_NOT_FOUND = "ZONE_NOT_FOUND"
    CONFIG_NOT_FOUND = "CONFIG_NOT_FOUND"
    INVALID_CONFIG = "INVALID_CONFIG"
    AUTHORITATIVE_NOT_FOUND = "AUTHORITATIVE_NOT_FOUND"
    TLD_NOT_FOUND = "TLD_NOT_FOUND"
