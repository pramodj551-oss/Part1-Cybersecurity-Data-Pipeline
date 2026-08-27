"""Regression tests for the data cleaning module."""

import pandas as pd
import pytest

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


def _valid_dataframe() -> pd.DataFrame:
    """Return a deterministic dataset matching the configured schema."""
    return pd.DataFrame(
        {
            "incident_id": ["INC-001", "INC-002", "INC-003"],
            "incident_date": ["2026-01-05", "2026-01-10", "2026-01-17"],
            "sector": ["Finance", "Healthcare", "Finance"],
            "region": ["West", "West", "North"],
            "attack_type": ["Ransomware", "Phishing", "Ransomware"],
            "threat_actor": ["Actor A", "Actor B", "Actor A"],
            "records_affected": [1000, 0, 500],
            "downtime_hours": [24, 12, 48],
            "ransom_demand_usd": [10000, 0, 25000],
            "detection_time_hours": [4, 8, 0],
            "severity_score": [8, 5, 9],
            "response_team_size": [5, 3, 7],
            "regulatory_fine_usd": [2000, 0, 5000],
            "resolved_within_7_days": [True, False, True],
            "data_exfiltration": [True, False, True],
            "zero_day_used": [False, False, True],
        }
    )


def test_data_cleaner_run_produces_valid_output():
    """Full cleaner run removes duplicate IDs and normalizes core datatypes."""
    dataframe = _valid_dataframe()
    duplicate = pd.concat([dataframe, dataframe.iloc[[0]]], ignore_index=True)

    cleaned = DataCleaner(duplicate).run()

    assert len(cleaned) == len(dataframe)
    assert cleaned["incident_id"].is_unique
    assert pd.api.types.is_datetime64_any_dtype(cleaned["incident_date"])
    assert not cleaned.isna().any().any()
    assert cleaned["severity_score"].between(0, 10).all()


def test_data_cleaner_rejects_invalid_incident_date():
    """Invalid incident dates must fail instead of being silently coerced."""
    dataframe = _valid_dataframe()
    dataframe.loc[0, "incident_date"] = "not-a-date"

    with pytest.raises(ValueError, match="invalid incident_date"):
        DataCleaner(dataframe).run()
