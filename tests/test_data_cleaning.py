import pandas as pd

from src.data_cleaning import DataCleaner


def test_normalize_text_preserves_security_acronyms():
    test_cases = {
        "ddos": "DDoS",
        "DDoS": "DDoS",
        "api": "API",
        "API": "API",
        "apt": "APT",
        "IoT": "IoT",
        "iot": "IoT",
        "sql injection": "SQL Injection",
        "ssh": "SSH",
        "vpn": "VPN",
        "xss": "XSS",
    }

    for input_value, expected_value in test_cases.items():
        assert DataCleaner.normalize_text(input_value) == expected_value


def test_normalize_text_cleans_whitespace():
    assert (
        DataCleaner.normalize_text("  financial   services  ")
        == "Financial Services"
    )


def test_normalize_text_handles_missing_values():
    assert DataCleaner.normalize_text(None) == "Unknown"
    assert DataCleaner.normalize_text(pd.NA) == "Unknown"


def test_normalize_text_handles_empty_values():
    assert DataCleaner.normalize_text("") == "Unknown"
    assert DataCleaner.normalize_text("   ") == "Unknown"
