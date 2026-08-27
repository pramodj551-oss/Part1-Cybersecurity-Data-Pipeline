"""Core regression and integration tests for the Part 1 pipeline."""

from pathlib import Path

import pandas as pd
import pytest

from src.config import DATABASE_TABLE, EXPECTED_COLUMNS
from src.data_cleaning import DataCleaner
from src.data_loader import DataLoader
from src.database import DatabaseManager
from src.feature_engineering import FeatureEngineer


@pytest.fixture
def valid_dataframe() -> pd.DataFrame:
    """Small deterministic dataset that exercises the core pipeline."""
    return pd.DataFrame(
        {
            "incident_id": ["INC-001", "INC-002", "INC-003"],
            "incident_date": ["2025-12-05", "2025-12-10", "2025-12-17"],
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
    """Loader accepts the complete schema and rejects missing columns."""
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
    """Feature engineering preserves rows and creates finite features."""
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
    """Ratio features remain finite when denominators are zero."""
    cleaned = DataCleaner(valid_dataframe).run()
    engineered = FeatureEngineer(cleaned).run()

    assert (engineered["ransom_per_record"] >= 0).all()
    assert (engineered["fine_per_record"] >= 0).all()
    assert (engineered["downtime_per_record"] >= 0).all()
    assert (engineered["response_efficiency"] >= 0).all()


def test_feature_engineering_rejects_non_finite_values(valid_dataframe):
    """Feature engineering must reject non-finite numeric input."""
    invalid = valid_dataframe.copy()
    invalid["records_affected"] = invalid["records_affected"].astype(float)
    invalid.loc[0, "records_affected"] = float("inf")

    cleaned = DataCleaner(invalid).run()

    with pytest.raises(ValueError, match="invalid numeric"):
        FeatureEngineer(cleaned).run()


def test_feature_engineering_rejects_future_incident_date(valid_dataframe):
    """Future incident dates must be rejected relative to the configured reference date."""
    invalid = valid_dataframe.copy()
    invalid.loc[0, "incident_date"] = "2099-01-01"

    cleaned = DataCleaner(invalid).run()

    with pytest.raises(ValueError, match="future"):
        FeatureEngineer(cleaned).run()


def test_expected_schema_is_complete(valid_dataframe):
    """Regression guard for accidental schema drift."""
    assert set(EXPECTED_COLUMNS).issubset(valid_dataframe.columns)


def test_data_loader_missing_file(tmp_path: Path):
    """Missing raw dataset must fail with a clear exception."""
    missing_file = tmp_path / "missing.csv"
    loader = DataLoader(file_path=missing_file)

    with pytest.raises(FileNotFoundError, match="Dataset not found"):
        loader.load_csv()


def test_database_round_trip_and_schema(valid_dataframe, tmp_path: Path):
    """Engineered data can be stored, validated and read back from SQLite."""
    cleaned = DataCleaner(valid_dataframe).run()
    engineered = FeatureEngineer(cleaned).run()

    manager = DatabaseManager(database_path=tmp_path / "integration.db")
    manager.connect()
    try:
        manager.create_table(engineered)
        manager.replace_table(engineered)
        manager.verify_table()
        manager.verify_dataframe_schema(engineered)

        assert manager.get_row_count() == len(engineered)
        preview = manager.preview_table(2)
        assert len(preview) == 2
        assert preview["incident_id"].is_unique

        kpi = manager.fetch_dataframe(
            f"SELECT COUNT(*) AS total FROM {DATABASE_TABLE}"
        )
        assert int(kpi.iloc[0]["total"]) == len(engineered)
    finally:
        manager.close()


def test_all_sql_queries_execute(valid_dataframe, tmp_path: Path):
    """Every documented SQL analytics query must execute against the current schema."""
    cleaned = DataCleaner(valid_dataframe).run()
    engineered = FeatureEngineer(cleaned).run()

    manager = DatabaseManager(database_path=tmp_path / "queries.db")
    manager.connect()
    try:
        manager.create_table(engineered)
        manager.replace_table(engineered)

        sql_text = Path("queries.sql").read_text(encoding="utf-8")
        statements = []
        for raw_statement in sql_text.split(";"):
            lines = [line for line in raw_statement.splitlines() if not line.strip().startswith("--")]
            statement = "\n".join(lines).strip()
            if statement:
                statements.append(statement)

        assert len(statements) == 29

        for index, statement in enumerate(statements, start=1):
            try:
                result = manager.fetch_dataframe(statement)
            except Exception as error:
                raise AssertionError(f"SQL query #{index} failed: {error}") from error
            assert isinstance(result, pd.DataFrame)
    finally:
        manager.close()
