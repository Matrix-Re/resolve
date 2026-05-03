def extract_zone_domain(requested_domain: str) -> str:
    """
    Extract the zone domain from a requested domain.

    Examples:
    - google.com -> google.com
    - maps.google.com -> google.com
    - exemple.maps.google.com -> google.com
    """
    clean_domain = requested_domain.strip().lower().removesuffix(".")
    parts = clean_domain.split(".")

    if len(parts) < 2:
        raise ValueError(f"Invalid domain name: {requested_domain}")

    return ".".join(parts[-2:])
