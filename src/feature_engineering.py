"""
Production feature engineering for the Cybersecurity Incident Analytics pipeline.

Author: Pramod Prakash Jadhav
"""

from __future__ import annotations

import logging
from typing import Any

import numpy as np
import pandas as pd

from src.config import EXPECTED_COLUMNS, LOG_FILE

logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(
        filename=LOG_FILE,
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )


class FeatureEngineer:
    """Create deterministic analytical features from cleaned incident data."""

    def __init__(self, dataframe: pd.DataFrame):
        if not isinstance(dataframe, pd.DataFrame):
            raise TypeError("dataframe must be a pandas DataFrame")
        self.df = dataframe.copy()
        logger.info("FeatureEngineer initialized with %d rows.", len(self.df))

    def validate_input(self) -> None:
        """Validate the cleaned dataset before feature generation."""
        if self.df.empty:
            raise ValueError("Input dataset is empty.")

        missing = [c for c in EXPECTED_COLUMNS if c not in self.df.columns]
        if missing:
            raise ValueError(f"Missing required input columns: {missing}")

        if self.df["incident_id"].isna().any():
            raise ValueError("incident_id contains missing values.")
        if self.df["incident_id"].duplicated().any():
            raise ValueError("incident_id contains duplicate values.")

        self.df["incident_date"] = pd.to_datetime(
            self.df["incident_date"], errors="coerce"
        )
        if self.df["incident_date"].isna().any():
            raise ValueError("incident_date contains invalid or missing values.")

        numeric_columns = [
            "records_affected", "downtime_hours", "ransom_demand_usd",
            "detection_time_hours", "severity_score", "response_team_size",
            "regulatory_fine_usd",
        ]
        for column in numeric_columns:
            numeric = pd.to_numeric(self.df[column], errors="coerce")
            if numeric.isna().any() or not np.isfinite(numeric.to_numpy()).all():
                raise ValueError(f"Column '{column}' contains invalid numeric values.")
            self.df[column] = numeric

        for column in ("resolved_within_7_days", "data_exfiltration", "zero_day_used"):
            if self.df[column].isna().any():
                raise ValueError(f"Boolean column '{column}' contains missing values.")
            self.df[column] = self.df[column].astype(bool)

        logger.info("Feature engineering input validation passed.")

    def create_date_features(self) -> None:
        date = self.df["incident_date"]
        self.df["incident_year"] = date.dt.year.astype(int)
        self.df["incident_month"] = date.dt.month.astype(int)
        self.df["incident_day"] = date.dt.day.astype(int)
        self.df["incident_week"] = date.dt.isocalendar().week.astype(int)
        self.df["incident_quarter"] = date.dt.quarter.astype(int)
        self.df["incident_weekday"] = date.dt.day_name()
        self.df["is_weekend"] = date.dt.weekday.isin([5, 6]).astype(int)
        self.df["month_name"] = date.dt.month_name()

    def create_incident_age(self) -> None:
        latest_date = self.df["incident_date"].max()
        self.df["incident_age_days"] = (latest_date - self.df["incident_date"]).dt.days

    def create_quarter_label(self) -> None:
        self.df["quarter_label"] = "Q" + self.df["incident_quarter"].astype(str)

    @staticmethod
    def _safe_ratio(numerator: pd.Series, denominator: pd.Series) -> pd.Series:
        """Return numerator/denominator; undefined zero-denominator ratios become 0."""
        result = numerator.div(denominator.replace(0, np.nan))
        return result.replace([np.inf, -np.inf], np.nan).fillna(0.0)

    def create_financial_features(self) -> None:
        self.df["ransom_per_record"] = self._safe_ratio(
            self.df["ransom_demand_usd"], self.df["records_affected"]
        ).round(2)
        self.df["fine_per_record"] = self._safe_ratio(
            self.df["regulatory_fine_usd"], self.df["records_affected"]
        ).round(2)
        self.df["total_financial_impact"] = (
            self.df["ransom_demand_usd"] + self.df["regulatory_fine_usd"]
        )

    def create_operational_features(self) -> None:
        self.df["downtime_per_record"] = self._safe_ratio(
            self.df["downtime_hours"], self.df["records_affected"]
        ).round(4)
        self.df["response_efficiency"] = self._safe_ratio(
            self.df["response_team_size"], self.df["detection_time_hours"]
        ).round(2)

        bins = [-np.inf, 6, 24, 72, np.inf]
        labels = ["Very Fast", "Fast", "Moderate", "Slow"]
        self.df["detection_speed"] = pd.cut(
            self.df["detection_time_hours"], bins=bins, labels=labels
        ).astype(str)

    def create_incident_cost_category(self) -> None:
        """Create stable quartile categories even when values have few unique levels."""
        values = self.df["total_financial_impact"]
        rank = values.rank(method="average", pct=True)
        self.df["incident_cost_category"] = pd.cut(
            rank,
            bins=[-np.inf, 0.25, 0.50, 0.75, np.inf],
            labels=["Low", "Medium", "High", "Critical"],
            include_lowest=True,
        ).astype(str)

    def create_threshold_flags(self) -> None:
        self.df["high_severity_flag"] = (self.df["severity_score"] >= 8).astype(int)
        self.df["high_ransom_flag"] = (
            self.df["ransom_demand_usd"] >= self.df["ransom_demand_usd"].median()
        ).astype(int)
        self.df["large_breach_flag"] = (
            self.df["records_affected"] >= self.df["records_affected"].median()
        ).astype(int)
        self.df["long_downtime_flag"] = (
            self.df["downtime_hours"] >= self.df["downtime_hours"].median()
        ).astype(int)

    def _add_frequency_feature(self, source: str, target: str) -> None:
        frequency = self.df[source].value_counts(dropna=False)
        self.df[target] = self.df[source].map(frequency).fillna(0).astype(int)

    def create_frequency_features(self) -> None:
        self._add_frequency_feature("sector", "sector_frequency")
        self._add_frequency_feature("region", "region_frequency")
        self._add_frequency_feature("attack_type", "attack_frequency")
        self._add_frequency_feature("threat_actor", "threat_actor_frequency")

    def create_scores(self) -> None:
        self.df["risk_score"] = (
            self.df["severity_score"] * 3
            + self.df["zero_day_used"].astype(int) * 2
            + self.df["data_exfiltration"].astype(int) * 2
            + self.df["high_ransom_flag"]
            + self.df["large_breach_flag"]
        )
        self.df["incident_complexity_score"] = (
            self.df["severity_score"]
            + np.log1p(self.df["records_affected"])
            + self.df["downtime_hours"] / 24
            + self.df["detection_time_hours"] / 24
        ).round(2)

    def validate_output(self, original_columns: list[str], original_rows: int) -> None:
        """Validate generated features and guard against accidental row loss/leakage."""
        if len(self.df) != original_rows:
            raise ValueError("Feature engineering changed the number of rows.")
        if self.df["incident_id"].duplicated().any():
            raise ValueError("Feature engineering introduced duplicate incident_id values.")
        if self.df.isna().any().any():
            missing = self.df.columns[self.df.isna().any()].tolist()
            raise ValueError(f"Feature engineering produced missing values: {missing}")

        numeric = self.df.select_dtypes(include=[np.number])
        if not np.isfinite(numeric.to_numpy()).all():
            raise ValueError("Feature engineering produced non-finite numeric values.")

        created = [c for c in self.df.columns if c not in original_columns]
        if not created:
            raise ValueError("No engineered features were created.")
        logger.info("Feature output validation passed: %d new features.", len(created))

    def run(self) -> pd.DataFrame:
        """Execute feature engineering in dependency-safe order."""
        logger.info("=" * 60)
        logger.info("Starting Feature Engineering Pipeline")
        logger.info("=" * 60)

        original_columns = self.df.columns.tolist()
        original_rows = len(self.df)

        self.validate_input()
        self.create_date_features()
        self.create_incident_age()
        self.create_quarter_label()
        self.create_financial_features()
        self.create_operational_features()
        self.create_incident_cost_category()
        self.create_threshold_flags()
        self.create_frequency_features()
        self.create_scores()
        self.validate_output(original_columns, original_rows)

        logger.info("Feature Engineering Pipeline Completed Successfully")
        return self.df


if __name__ == "__main__":
    from src.config import CLEAN_DATA_FILE

    try:
        clean_df = pd.read_csv(CLEAN_DATA_FILE, parse_dates=["incident_date"])
        engineered_df = FeatureEngineer(clean_df).run()
        print("\n" + "=" * 70)
        print("FEATURE ENGINEERING PIPELINE COMPLETED")
        print("=" * 70)
        print(f"Rows    : {len(engineered_df)}")
        print(f"Columns : {len(engineered_df.columns)}")
        print("=" * 70)
    except Exception as error:
        logger.exception("Feature Engineering Pipeline Failed.")
        print("\nPipeline Error")
        print(error)
        raise
