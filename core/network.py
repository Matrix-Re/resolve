def parse_server_address(address: str) -> tuple[str, int]:
    """
    Parse a server address formatted as host:port.

    Example:
    - 127.0.0.1:5302 -> ("127.0.0.1", 5302)
    """
    if not address or ":" not in address:
        raise ValueError(f"Invalid server address: {address}")

    host, port = address.rsplit(":", 1)

    if not host:
        raise ValueError(f"Invalid server host: {address}")

    if not port.isdigit():
        raise ValueError(f"Invalid server port: {address}")

    return host, int(port)
