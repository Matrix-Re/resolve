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


def extract_domain_suffix(requested_domain: str) -> str:
    """
    Extract the domain suffix from a requested domain.

    Examples:
    - google.com -> .com
    - maps.google.com -> .com
    - exemple.maps.google.com -> .com
    - google.fr -> .fr
    """
    clean_domain = requested_domain.strip().lower().removesuffix(".")
    parts = [part for part in clean_domain.split(".") if part]

    if len(parts) < 2:
        raise ValueError(f"Invalid domain name: {requested_domain}")

    return f".{parts[-1]}"
