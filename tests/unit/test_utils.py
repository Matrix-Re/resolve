import pytest

from core.utils import extract_zone_domain, extract_domain_suffix


@pytest.mark.parametrize(
    ("requested_domain", "expected_zone", "expected_suffix"),
    [
        ("google.com", "google.com", ".com"),
        ("maps.google.com", "google.com", ".com"),
        ("photos.google.com", "google.com", ".com"),
        ("example.maps.google.com", "google.com", ".com"),
        ("GOOGLE.COM", "google.com", ".com"),
        ("maps.google.com.", "google.com", ".com"),
        ("  maps.google.com  ", "google.com", ".com"),
        ("free.fr", "free.fr", ".fr"),
        ("api.free.fr", "free.fr", ".fr"),
    ],
)
def test_extract_zone_domain(
    requested_domain: str, expected_zone: str, expected_suffix: str
) -> None:
    assert extract_zone_domain(requested_domain) == expected_zone
    assert extract_domain_suffix(requested_domain) == expected_suffix


@pytest.mark.parametrize(
    "invalid_domain",
    [
        "",
        "localhost",
        "com",
        ".",
        "   ",
    ],
)
def test_extract_zone_domain_with_invalid_domain(invalid_domain: str) -> None:
    with pytest.raises(ValueError):
        extract_zone_domain(invalid_domain)
        extract_domain_suffix(invalid_domain)
