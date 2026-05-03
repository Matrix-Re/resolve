import pytest

from core.utils import extract_zone_domain


@pytest.mark.parametrize(
    ("requested_domain", "expected_zone"),
    [
        ("google.com", "google.com"),
        ("maps.google.com", "google.com"),
        ("photos.google.com", "google.com"),
        ("example.maps.google.com", "google.com"),
        ("GOOGLE.COM", "google.com"),
        ("maps.google.com.", "google.com"),
        ("  maps.google.com  ", "google.com"),
    ],
)
def test_extract_zone_domain(requested_domain: str, expected_zone: str) -> None:
    assert extract_zone_domain(requested_domain) == expected_zone


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
