"""Core regression tests for the Part 1 cybersecurity data pipeline."""

from pathlib import Path

import pandas as pd
import pytest

from src.config import EXPECTED_COLUMNS
from src.data_cleaning import DataCleaner
from src.data_loader import DataLoader
from src.feature_engineering import FeatureEngineer


@pytest.fixture
def valid_dataframe() -> pd.DataFrame:
    """Small deterministic dataset that exercises the core pipeline."""
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


def test_data_loader_schema_validation(valid_dataframe):
    """Loader accepts the complete required schema and rejects missing columns."""
    DataLoader.validate_empty(valid_dataframe)
    DataLoader.validate_schema(valid_dataframe)

    incomplete = valid_dataframe.drop(columns=["region"])
    with pytest.raises(ValueError, match="Missing Columns"):
        DataLoader.validate_schema(incomplete)


def test_data_cleaner_produces_valid_output(valid_dataframe):
    """Cleaner removes duplicates and normalizes core datatypes."""
    duplicate = pd.concat([valid_dataframe, valid_dataframe.iloc[[0]]], ignore_index=True)
    cleaned = DataCleaner(duplicate).run()

    assert len(cleaned) == len(valid_dataframe)
    assert cleaned["incident_id"].is_unique
    assert pd.api.types.is_datetime64_any_dtype(cleaned["incident_date"])
    assert not cleaned.isna().any().any()
    assert cleaned["severity_score"].between(0, 10).all()


def test_feature_engineering_preserves_rows_and_creates_features(valid_dataframe):
    """Feature engineering preserves row count and creates finite features."""
    cleaned = DataCleaner(valid_dataframe).run()
    engineered = FeatureEngineer(cleaned).run()

    assert len(engineered) == len(cleaned)
    assert engineered["incident_id"].is_unique
    assert "risk_score" in engineered.columns
    assert "incident_complexity_score" in engineered.columns
    assert "total_financial_impact" in engineered.columns
    assert not engineered.isna().any().any()

    numeric = engineered.select_dtypes(include="number")
    assert numeric.apply(lambda col: col.map(pd.notna).all()).all()


def test_feature_engineering_handles_zero_denominators(valid_dataframe):
    """Ratio features must remain finite when denominators are zero."""
    cleaned = DataCleaner(valid_dataframe).run()
    engineered = FeatureEngineer(cleaned).run()

    assert (engineered["ransom_per_record"] >= 0).all()
    assert (engineered["fine_per_record"] >= 0).all()
    assert (engineered["downtime_per_record"] >= 0).all()
    assert (engineered["response_efficiency"] >= 0).all()


def test_expected_schema_is_complete(valid_dataframe):
    """Regression guard for accidental schema drift."""
    assert set(EXPECTED_COLUMNS).issubset(valid_dataframe.columns)


def test_data_loader_missing_file(tmp_path: Path):
    """Missing raw dataset must fail with a clear exception."""
    missing_file = tmp_path / "missing.csv"
    loader = DataLoader(file_path=missing_file)

    with pytest.raises(FileNotFoundError, match="Dataset not found"):
        loader.load_csv()
