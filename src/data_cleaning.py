
"""
Data Cleaning Module

Performs production-grade cleaning and validation
for the Cybersecurity Incident Reports dataset.

Author:
Pramod Prakash Jadhav
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


# ==========================================================
# Logger Configuration
# ==========================================================

logger = logging.getLogger(__name__)

if not logger.handlers:
    logging.basicConfig(
        filename=LOG_FILE,
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )


class DataCleaner:
    """
    Production-grade data cleaning and validation pipeline.

    Responsibilities
    ----------------
    - Required-column validation
    - Missing value handling
    - Duplicate removal
    - Datatype conversion
    - Strict boolean normalization
    - Date validation
    - Category standardization
    - Numeric validation
    - Range validation
    - Outlier treatment
    - Final dataset validation
    """

    def __init__(self, dataframe: pd.DataFrame):

        self.df = dataframe.copy()

        self.report: dict[str, Any] = {
            "initial_rows": len(self.df),
            "final_rows": 0,
            "duplicates_removed": 0,
            "missing_values_filled": 0,
            "outliers_capped": 0,
        }

        logger.info(
            "DataCleaner initialized with %d rows.",
            len(self.df),
        )

    # ======================================================
    # Schema Validation
    # ======================================================

    def validate_required_columns(self) -> None:
        """
        Validate that all expected dataset columns exist.
        """

        logger.info("Validating required columns...")

        missing_columns = [
            column
            for column in EXPECTED_COLUMNS
            if column not in self.df.columns
        ]

        if missing_columns:
            raise ValueError(
                f"Missing required columns: {missing_columns}"
            )

        logger.info(
            "Required-column validation completed."
        )

    # ======================================================
    # Helper Methods
    # ======================================================

    @staticmethod
    def normalize_text(value: Any) -> str:
        """
        Normalize text values.

        Example:
        ' finance ' -> 'Finance'
        """

        if pd.isna(value):
            return DEFAULT_CATEGORICAL_VALUE

        return (
            str(value)
            .strip()
            .title()
        )

    @staticmethod
    def convert_boolean(value: Any) -> bool:
        """
        Convert supported boolean representations.

        Accepted values:
        True / False
        true / false
        yes / no
        y / n
        t / f
        1 / 0

        Invalid values raise ValueError instead of
        silently converting to False.
        """

        if pd.isna(value):
            return bool(DEFAULT_BOOLEAN_VALUE)

        if isinstance(value, bool):
            return value

        if isinstance(value, (int, float)) and value in (0, 1):
            return bool(value)

        normalized = (
            str(value)
            .strip()
            .lower()
        )

        if normalized in {
            "true",
            "t",
            "yes",
            "y",
            "1",
        }:
            return True

        if normalized in {
            "false",
            "f",
            "no",
            "n",
            "0",
        }:
            return False

        raise ValueError(
            f"Invalid boolean value: {value!r}. "
            "Expected true/false, yes/no, or 1/0."
        )

    @staticmethod
    def cap_outliers(
        series: pd.Series,
    ) -> tuple[pd.Series, int]:
        """
        Cap statistical outliers using IQR.
        """

        q1 = series.quantile(0.25)
        q3 = series.quantile(0.75)

        iqr = q3 - q1

        if pd.isna(iqr) or iqr == 0:
            return series, 0

        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr

        capped = series.clip(
            lower=lower,
            upper=upper,
        )

        count = int(
            (series != capped).sum()
        )

        return capped, count

    # ======================================================
    # Dataset Statistics
    # ======================================================

    def dataset_statistics(self) -> None:
        """
        Print basic dataset statistics.
        """

        print("\n" + "=" * 60)
        print("DATA CLEANING SUMMARY")
        print("=" * 60)

        print(
            f"Rows    : {len(self.df)}"
        )

        print(
            f"Columns : {len(self.df.columns)}"
        )

        print("\nMissing Values\n")

        print(
            self.df.isna().sum()
        )

        print("=" * 60)

    # ======================================================
    # Save Quality Report
    # ======================================================

    def save_quality_report(self) -> None:
        """
        Save cleaning quality report as JSON.
        """

        self.report["final_rows"] = len(
            self.df
        )

        QUALITY_REPORT_FILE.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with open(
            QUALITY_REPORT_FILE,
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                self.report,
                file,
                indent=4,
            )

        logger.info(
            "Cleaning report saved to %s.",
            QUALITY_REPORT_FILE,
        )

    # ======================================================
    # Remove Duplicate Records
    # ======================================================

    def remove_duplicates(self) -> None:
        """
        Remove duplicate records based on incident_id.
        """

        logger.info(
            "Removing duplicate records..."
        )

        if "incident_id" not in self.df.columns:
            raise ValueError(
                "Required column 'incident_id' is missing."
            )

        before = len(self.df)

        self.df = self.df.drop_duplicates(
            subset=["incident_id"],
            keep="first",
        ).copy()

        removed = before - len(self.df)

        self.report[
            "duplicates_removed"
        ] = removed

        logger.info(
            "%d duplicate records removed.",
            removed,
        )

    # ======================================================
    # Handle Missing Values
    # ======================================================

    def handle_missing_values(self) -> None:
        """
        Fill missing values according to column type.
        """

        logger.info(
            "Handling missing values..."
        )

        missing_before = int(
            self.df.isna()
            .sum()
            .sum()
        )

        # --------------------------------------------------
        # Categorical Columns
        # --------------------------------------------------

        for column in CATEGORICAL_COLUMNS:

            if column in self.df.columns:

                self.df[column] = (
                    self.df[column]
                    .fillna(
                        DEFAULT_CATEGORICAL_VALUE
                    )
                    .apply(
                        self.normalize_text
                    )
                )

        # --------------------------------------------------
        # Numeric Columns
        # --------------------------------------------------

        for column in NUMERIC_COLUMNS:

            if column not in self.df.columns:
                continue

            numeric = pd.to_numeric(
                self.df[column],
                errors="coerce",
            )

            invalid_mask = (
                self.df[column].notna()
                & numeric.isna()
            )

            if invalid_mask.any():

                count = int(
                    invalid_mask.sum()
                )

                raise ValueError(
                    f"Column '{column}' contains "
                    f"{count} invalid numeric value(s)."
                )

            median_value = numeric.median()

            if pd.isna(median_value):
                median_value = (
                    DEFAULT_NUMERIC_VALUE
                )

            self.df[column] = (
                numeric.fillna(
                    median_value
                )
            )

        # --------------------------------------------------
        # Boolean Columns
        # --------------------------------------------------

        for column in BOOLEAN_COLUMNS:

            if column in self.df.columns:

                self.df[column] = (
                    self.df[column]
                    .apply(
                        self.convert_boolean
                    )
                    .astype(bool)
                )

        missing_after = int(
            self.df.isna()
            .sum()
            .sum()
        )

        self.report[
            "missing_values_filled"
        ] = (
            missing_before
            - missing_after
        )

        logger.info(
            "Missing value handling completed."
        )

    # ======================================================
    # Parse Incident Date
    # ======================================================

    def parse_incident_date(self) -> None:
        """
        Convert incident_date to datetime format
        and reject invalid non-null values.
        """

        if "incident_date" not in self.df.columns:

            raise ValueError(
                "Required column 'incident_date' "
                "is missing."
            )

        logger.info(
            "Parsing incident_date..."
        )

        original_dates = (
            self.df["incident_date"]
        )

        parsed_dates = pd.to_datetime(
            original_dates,
            errors="coerce",
        )

        invalid_dates = (
            original_dates.notna()
            & parsed_dates.isna()
        )

        if invalid_dates.any():

            count = int(
                invalid_dates.sum()
            )

            examples = (
                original_dates[
                    invalid_dates
                ]
                .head(5)
                .tolist()
            )

            raise ValueError(
                f"Found {count} invalid "
                f"incident_date value(s). "
                f"Examples: {examples}"
            )

        self.df["incident_date"] = (
            parsed_dates
        )

        logger.info(
            "Datetime conversion completed."
        )

    # ======================================================
    # Validate Numeric Columns
    # ======================================================

    def validate_numeric_columns(self) -> None:
        """
        Ensure numeric columns contain valid numeric values.
        """

        logger.info(
            "Validating numeric columns..."
        )

        for column in NUMERIC_COLUMNS:

            if column not in self.df.columns:
                continue

            numeric = pd.to_numeric(
                self.df[column],
                errors="coerce",
            )

            invalid_mask = (
                self.df[column].notna()
                & numeric.isna()
            )

            if invalid_mask.any():

                count = int(
                    invalid_mask.sum()
                )

                raise ValueError(
                    f"Column '{column}' contains "
                    f"{count} invalid numeric value(s)."
                )

            self.df[column] = (
                numeric.fillna(
                    DEFAULT_NUMERIC_VALUE
                )
            )

        logger.info(
            "Numeric validation completed."
        )

    # ======================================================
    # Standardize Categorical Columns
    # ======================================================

    def standardize_categories(self) -> None:
        """
        Standardize categorical columns.
        """

        logger.info(
            "Standardizing categorical columns..."
        )

        for column in CATEGORICAL_COLUMNS:

            if column not in self.df.columns:
                continue

            self.df[column] = (
                self.df[column]
                .apply(
                    self.normalize_text
                )
            )

        logger.info(
            "Categorical standardization completed."
        )

    # ======================================================
    # Normalize Boolean Columns
    # ======================================================

    def normalize_boolean_columns(self) -> None:
        """
        Normalize all configured boolean columns.
        """

        logger.info(
            "Normalizing boolean columns..."
        )

        for column in BOOLEAN_COLUMNS:

            if column not in self.df.columns:
                continue

            self.df[column] = (
                self.df[column]
                .apply(
                    self.convert_boolean
                )
                .astype(bool)
            )

        logger.info(
            "Boolean normalization completed."
        )

    # ======================================================
    # Range Validation
    # ======================================================

    def validate_ranges(self) -> None:
        """
        Enforce configured numeric limits.
        """

        logger.info(
            "Validating numeric ranges..."
        )

        if "severity_score" in self.df.columns:

            self.df[
                "severity_score"
            ] = self.df[
                "severity_score"
            ].clip(
                lower=0,
                upper=MAX_SEVERITY_SCORE,
            )

        if "downtime_hours" in self.df.columns:

            self.df[
                "downtime_hours"
            ] = self.df[
                "downtime_hours"
            ].clip(
                lower=0,
                upper=MAX_DOWNTIME_HOURS,
            )

        if "detection_time_hours" in self.df.columns:

            self.df[
                "detection_time_hours"
            ] = self.df[
                "detection_time_hours"
            ].clip(
                lower=0,
            )

        if "response_team_size" in self.df.columns:

            self.df[
                "response_team_size"
            ] = self.df[
                "response_team_size"
            ].clip(
                lower=1,
                upper=MAX_RESPONSE_TEAM_SIZE,
            )

        if "records_affected" in self.df.columns:

            self.df[
                "records_affected"
            ] = self.df[
                "records_affected"
            ].clip(
                lower=0,
            )

        if "ransom_demand_usd" in self.df.columns:

            self.df[
                "ransom_demand_usd"
            ] = self.df[
                "ransom_demand_usd"
            ].clip(
                lower=0,
            )

        if "regulatory_fine_usd" in self.df.columns:

            self.df[
                "regulatory_fine_usd"
            ] = self.df[
                "regulatory_fine_usd"
            ].clip(
                lower=0,
            )

        logger.info(
            "Range validation completed."
        )

    # ======================================================
    # Handle Outliers
    # ======================================================

    def handle_outliers(self) -> None:
        """
        Cap statistical outliers using IQR.
        """

        logger.info(
            "Handling outliers..."
        )

        total_outliers = 0

        for column in NUMERIC_COLUMNS:

            if column not in self.df.columns:
                continue

            cleaned_series, capped = (
                self.cap_outliers(
                    self.df[column]
                )
            )

            self.df[column] = (
                cleaned_series
            )

            total_outliers += capped

        self.report[
            "outliers_capped"
        ] = total_outliers

        logger.info(
            "%d outlier values capped.",
            total_outliers,
        )

    # ======================================================
    # Final Dataset Validation
    # ======================================================

   missing_columns = [
    column
    for column in EXPECTED_COLUMNS
    if column not in self.df.columns
]

if missing_columns:
    raise ValueError(
        f"Missing required columns after cleaning: {missing_columns}"
    ) 
    def final_validation(self) -> None:
        """
        Perform strict final validation.
        """

        logger.info(
            "Running final validation..."
        )

        if self.df.empty:

            raise ValueError(
                "Dataset became empty "
                "after cleaning."
            )

        if "incident_id" not in self.df.columns:

            raise ValueError(
                "Required column 'incident_id' "
                "is missing."
            )

        duplicate_count = int(
            self.df[
                "incident_id"
            ]
            .duplicated()
            .sum()
        )

        if duplicate_count > 0:

            raise ValueError(
                f"{duplicate_count} duplicate "
                "incident_id value(s) remain."
            )

        missing_values = int(
            self.df
            .isna()
            .sum()
            .sum()
        )

        if missing_values > 0:

            raise ValueError(
                f"{missing_values} missing "
                "value(s) remain after cleaning."
            )

        logger.info(
            "Final validation completed successfully."
        )

    # ======================================================
    # Save Clean Dataset
    # ======================================================

    def save_clean_dataset(self) -> None:
        """
        Save cleaned dataset.
        """

        logger.info(
            "Saving cleaned dataset..."
        )

        CLEAN_DATA_FILE.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.df.to_csv(
            CLEAN_DATA_FILE,
            index=False,
        )

        logger.info(
            "Clean dataset saved to %s",
            CLEAN_DATA_FILE,
        )

    # ======================================================
    # Execute Complete Cleaning Pipeline
    # ======================================================

    def run(self) -> pd.DataFrame:
        """
        Execute complete data cleaning pipeline.
        """

        logger.info("=" * 60)
        logger.info(
            "Starting Data Cleaning Pipeline"
        )
        logger.info("=" * 60)

        self.validate_required_columns()

        self.remove_duplicates()

        self.handle_missing_values()

        self.parse_incident_date()

        self.validate_numeric_columns()

        self.standardize_categories()

        self.normalize_boolean_columns()

        self.handle_outliers()

        self.validate_ranges()

        self.final_validation()

        self.dataset_statistics()

        self.save_quality_report()

        self.save_clean_dataset()

        logger.info("=" * 60)
        logger.info(
            "Data Cleaning Pipeline Completed Successfully"
        )
        logger.info("=" * 60)

        return self.df


# ==========================================================
# Standalone Execution
# ==========================================================

if __name__ == "__main__":

    from src.data_loader import DataLoader

    try:

        logger.info(
            "Loading raw dataset..."
        )

        loader = DataLoader()

        raw_df = loader.run()

        logger.info(
            "Running Data Cleaning Pipeline..."
        )

        cleaner = DataCleaner(
            raw_df
        )

        clean_df = cleaner.run()

        print(
            "\n"
            + "=" * 70
        )

        print(
            "DATA CLEANING PIPELINE COMPLETED"
        )

        print(
            "=" * 70
        )

        print(
            f"Rows              : "
            f"{len(clean_df)}"
        )

        print(
            f"Columns           : "
            f"{len(clean_df.columns)}"
        )

        print(
            f"Clean Dataset     : "
            f"{CLEAN_DATA_FILE}"
        )

        print(
            f"Quality Report    : "
            f"{QUALITY_REPORT_FILE}"
        )

        print(
            "=" * 70
        )

    except Exception as error:

        logger.exception(
            "Data Cleaning Pipeline Failed."
        )

        print(
            "\nPipeline Error"
        )

        print(error)
