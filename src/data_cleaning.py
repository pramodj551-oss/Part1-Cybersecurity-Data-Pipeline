"""
Data Cleaning Module

Production-grade cleaning and validation for the Cybersecurity Incident
Reports dataset.

Author: Pramod Prakash Jadhav
"""

from __future__ import annotations

import json
import logging
from typing import Any

import pandas as pd

from src.config import (
    BOOLEAN_COLUMNS,
    CATEGORICAL_COLUMNS,
    CLEAN_DATA_FILE,
    DEFAULT_BOOLEAN_VALUE,
    DEFAULT_CATEGORICAL_VALUE,
    DEFAULT_NUMERIC_VALUE,
    EXPECTED_COLUMNS,
    LOG_FILE,
    MAX_DOWNTIME_HOURS,
    MAX_RESPONSE_TEAM_SIZE,
    MAX_SEVERITY_SCORE,
    NUMERIC_COLUMNS,
    QUALITY_REPORT_FILE,
)

logger = logging.getLogger(__name__)

if not logger.handlers:
    logging.basicConfig(
        filename=LOG_FILE,
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )


class DataCleaner:
    """Production-grade data cleaning and validation pipeline."""

    def __init__(self, dataframe: pd.DataFrame):
        self.df = dataframe.copy()
        self.report: dict[str, Any] = {
            "initial_rows": len(self.df),
            "final_rows": 0,
            "duplicates_removed": 0,
            "missing_values_filled": 0,
            "outliers_capped": 0,
            "outliers_capped_by_column": {},
            "range_adjustments_by_column": {},
        }
        logger.info("DataCleaner initialized with %d rows.", len(self.df))

    def validate_required_columns(self) -> None:
        """Validate that all expected dataset columns exist."""
        missing_columns = [
            column for column in EXPECTED_COLUMNS if column not in self.df.columns
        ]
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")
        logger.info("Required-column validation completed.")

    @staticmethod
    def normalize_text(value: Any) -> str:
        """Normalize categorical text values."""
        if pd.isna(value):
            return DEFAULT_CATEGORICAL_VALUE
        return str(value).strip().title()

    @staticmethod
    def convert_boolean(value: Any) -> bool:
        """Convert supported boolean representations; reject invalid values."""
        if pd.isna(value):
            return bool(DEFAULT_BOOLEAN_VALUE)
        if isinstance(value, bool):
            return value
        if isinstance(value, (int, float)) and value in (0, 1):
            return bool(value)

        normalized = str(value).strip().lower()
        if normalized in {"true", "t", "yes", "y", "1"}:
            return True
        if normalized in {"false", "f", "no", "n", "0"}:
            return False

        raise ValueError(
            f"Invalid boolean value: {value!r}. "
            "Expected true/false, yes/no, y/n, t/f, or 1/0."
        )

    @staticmethod
    def cap_outliers(series: pd.Series) -> tuple[pd.Series, int]:
        """Cap statistical outliers using the IQR method."""
        q1 = series.quantile(0.25)
        q3 = series.quantile(0.75)
        iqr = q3 - q1

        if pd.isna(iqr) or iqr == 0:
            return series, 0

        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr
        capped = series.clip(lower=lower, upper=upper)
        count = int((series != capped).sum())
        return capped, count

    def dataset_statistics(self) -> None:
        """Print basic dataset statistics."""
        print("\n" + "=" * 60)
        print("DATA CLEANING SUMMARY")
        print("=" * 60)
        print(f"Rows    : {len(self.df)}")
        print(f"Columns : {len(self.df.columns)}")
        print("\nMissing Values\n")
        print(self.df.isna().sum())
        print("=" * 60)

    def save_quality_report(self) -> None:
        """Save cleaning quality report as JSON."""
        self.report["final_rows"] = len(self.df)
        QUALITY_REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(QUALITY_REPORT_FILE, "w", encoding="utf-8") as file:
            json.dump(self.report, file, indent=4)
        logger.info("Cleaning report saved to %s.", QUALITY_REPORT_FILE)

    def remove_duplicates(self) -> None:
        """Remove duplicate records based on incident_id."""
        if "incident_id" not in self.df.columns:
            raise ValueError("Required column 'incident_id' is missing.")

        before = len(self.df)
        self.df = self.df.drop_duplicates(
            subset=["incident_id"], keep="first"
        ).copy()
        removed = before - len(self.df)
        self.report["duplicates_removed"] = removed
        logger.info("%d duplicate records removed.", removed)

    def handle_missing_values(self) -> None:
        """Fill missing values according to configured column types."""
        missing_before = int(self.df.isna().sum().sum())

        for column in CATEGORICAL_COLUMNS:
            if column in self.df.columns:
                self.df[column] = (
                    self.df[column]
                    .fillna(DEFAULT_CATEGORICAL_VALUE)
                    .apply(self.normalize_text)
                )

        for column in NUMERIC_COLUMNS:
            if column not in self.df.columns:
                continue
            numeric = pd.to_numeric(self.df[column], errors="coerce")
            invalid_mask = self.df[column].notna() & numeric.isna()
            if invalid_mask.any():
                count = int(invalid_mask.sum())
                raise ValueError(
                    f"Column '{column}' contains {count} invalid numeric value(s)."
                )
            median_value = numeric.median()
            if pd.isna(median_value):
                median_value = DEFAULT_NUMERIC_VALUE
            self.df[column] = numeric.fillna(median_value)

        for column in BOOLEAN_COLUMNS:
            if column in self.df.columns:
                self.df[column] = (
                    self.df[column].apply(self.convert_boolean).astype(bool)
                )

        missing_after = int(self.df.isna().sum().sum())
        self.report["missing_values_filled"] = missing_before - missing_after
        logger.info("Missing value handling completed.")

    def parse_incident_date(self) -> None:
        """Convert incident_date to datetime and reject invalid non-null values."""
        if "incident_date" not in self.df.columns:
            raise ValueError("Required column 'incident_date' is missing.")

        original_dates = self.df["incident_date"]
        parsed_dates = pd.to_datetime(original_dates, errors="coerce")
        invalid_dates = original_dates.notna() & parsed_dates.isna()

        if invalid_dates.any():
            count = int(invalid_dates.sum())
            examples = original_dates[invalid_dates].head(5).tolist()
            raise ValueError(
                f"Found {count} invalid incident_date value(s). "
                f"Examples: {examples}"
            )

        self.df["incident_date"] = parsed_dates
        logger.info("Datetime conversion completed.")

    def validate_numeric_columns(self) -> None:
        """Ensure numeric columns contain valid numeric values."""
        for column in NUMERIC_COLUMNS:
            if column not in self.df.columns:
                continue
            numeric = pd.to_numeric(self.df[column], errors="coerce")
            invalid_mask = self.df[column].notna() & numeric.isna()
            if invalid_mask.any():
                count = int(invalid_mask.sum())
                raise ValueError(
                    f"Column '{column}' contains {count} invalid numeric value(s)."
                )
            self.df[column] = numeric.fillna(DEFAULT_NUMERIC_VALUE)
        logger.info("Numeric validation completed.")

    def standardize_categories(self) -> None:
        """Standardize configured categorical columns."""
        for column in CATEGORICAL_COLUMNS:
            if column in self.df.columns:
                self.df[column] = self.df[column].apply(self.normalize_text)
        logger.info("Categorical standardization completed.")

    def normalize_boolean_columns(self) -> None:
        """Normalize all configured boolean columns."""
        for column in BOOLEAN_COLUMNS:
            if column in self.df.columns:
                self.df[column] = (
                    self.df[column].apply(self.convert_boolean).astype(bool)
                )
        logger.info("Boolean normalization completed.")

    def validate_ranges(self) -> None:
        """Enforce configured numeric business-rule limits and report changes."""
        adjustments: dict[str, int] = {}

        def clip_and_count(
            column: str,
            lower: float | None = None,
            upper: float | None = None,
        ) -> None:
            if column not in self.df.columns:
                return

            original = self.df[column].copy()
            cleaned = original.clip(lower=lower, upper=upper)
            changed = int((original != cleaned).sum())
            self.df[column] = cleaned

            if changed:
                adjustments[column] = changed

        clip_and_count(
            "severity_score",
            lower=0,
            upper=MAX_SEVERITY_SCORE,
        )
        clip_and_count(
            "downtime_hours",
            lower=0,
            upper=MAX_DOWNTIME_HOURS,
        )
        clip_and_count(
            "detection_time_hours",
            lower=0,
        )
        clip_and_count(
            "response_team_size",
            lower=1,
            upper=MAX_RESPONSE_TEAM_SIZE,
        )
        clip_and_count("records_affected", lower=0)
        clip_and_count("ransom_demand_usd", lower=0)
        clip_and_count("regulatory_fine_usd", lower=0)

        self.report["range_adjustments_by_column"] = adjustments
        logger.info(
            "Range validation completed. Adjustments: %s",
            adjustments,
        )

    def handle_outliers(self) -> None:
        """Cap IQR outliers only for unbounded monetary/impact metrics."""
        # These columns have explicit business limits and should not be
        # statistically capped after range validation.
        outlier_columns = {
            "records_affected",
            "ransom_demand_usd",
            "regulatory_fine_usd",
        }

        total_outliers = 0
        capped_by_column: dict[str, int] = {}

        for column in NUMERIC_COLUMNS:
            if column not in self.df.columns:
                continue
            if column not in outlier_columns:
                continue

            cleaned_series, capped = self.cap_outliers(self.df[column])
            self.df[column] = cleaned_series
            total_outliers += capped

            if capped:
                capped_by_column[column] = capped

        self.report["outliers_capped"] = total_outliers
        self.report["outliers_capped_by_column"] = capped_by_column

        logger.info(
            "%d statistical outlier values capped: %s",
            total_outliers,
            capped_by_column,
        )

    def final_validation(self) -> None:
        """Perform strict final validation before saving."""
        missing_columns = [
            column for column in EXPECTED_COLUMNS if column not in self.df.columns
        ]
        if missing_columns:
            raise ValueError(
                f"Missing required columns after cleaning: {missing_columns}"
            )

        if self.df.empty:
            raise ValueError("Dataset became empty after cleaning.")

        if self.df["incident_id"].isna().any():
            raise ValueError("incident_id contains missing values.")

        duplicate_count = int(self.df["incident_id"].duplicated().sum())
        if duplicate_count > 0:
            raise ValueError(
                f"{duplicate_count} duplicate incident_id value(s) remain."
            )

        missing_values = int(self.df.isna().sum().sum())
        if missing_values > 0:
            raise ValueError(
                f"{missing_values} missing value(s) remain after cleaning."
            )

        logger.info("Final validation completed successfully.")

    def save_clean_dataset(self) -> None:
        """Save cleaned dataset to the configured processed path."""
        CLEAN_DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
        self.df.to_csv(CLEAN_DATA_FILE, index=False)
        logger.info("Clean dataset saved to %s", CLEAN_DATA_FILE)

    def run(self) -> pd.DataFrame:
        """Execute the complete data cleaning pipeline."""
        logger.info("=" * 60)
        logger.info("Starting Data Cleaning Pipeline")
        logger.info("=" * 60)

        self.validate_required_columns()
        self.remove_duplicates()
        self.handle_missing_values()
        self.parse_incident_date()
        self.validate_numeric_columns()
        self.standardize_categories()
        self.normalize_boolean_columns()

        # Business-rule limits are applied before statistical outlier treatment.
        self.validate_ranges()
        self.handle_outliers()

        self.final_validation()
        self.dataset_statistics()
        self.save_quality_report()
        self.save_clean_dataset()

        logger.info("Data Cleaning Pipeline Completed Successfully")
        return self.df


if __name__ == "__main__":
    from src.data_loader import DataLoader

    try:
        logger.info("Loading raw dataset...")
        loader = DataLoader()
        raw_df = loader.run()

        logger.info("Running Data Cleaning Pipeline...")
        cleaner = DataCleaner(raw_df)
        clean_df = cleaner.run()

        print("\n" + "=" * 70)
        print("DATA CLEANING PIPELINE COMPLETED")
        print("=" * 70)
        print(f"Rows              : {len(clean_df)}")
        print(f"Columns           : {len(clean_df.columns)}")
        print(f"Clean Dataset     : {CLEAN_DATA_FILE}")
        print(f"Quality Report    : {QUALITY_REPORT_FILE}")
        print("=" * 70)

    except Exception as error:
        logger.exception("Data Cleaning Pipeline Failed.")
        print("\nPipeline Error")
        print(error)
