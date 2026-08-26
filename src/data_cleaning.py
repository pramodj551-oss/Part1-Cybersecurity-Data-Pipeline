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
from typing import Dict

import pandas as pd

from src.config import (
    BOOLEAN_COLUMNS,
    CATEGORICAL_COLUMNS,
    CLEAN_DATA_FILE,
    DEFAULT_BOOLEAN_VALUE,
    DEFAULT_CATEGORICAL_VALUE,
    DEFAULT_NUMERIC_VALUE,
    LOG_FILE,
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
    Production-grade data cleaning pipeline.

    Responsibilities
    ----------------
    - Missing value handling
    - Duplicate removal
    - Datatype conversion
    - Boolean normalization
    - Category standardization
    - Numeric validation
    - Outlier treatment
    """

    def __init__(self, dataframe: pd.DataFrame):

        self.df = dataframe.copy()

        self.report: Dict = {
            "initial_rows": len(dataframe),
            "final_rows": 0,
            "duplicates_removed": 0,
            "missing_values_filled": 0,
            "outliers_capped": 0,
        }

        logger.info(
            "DataCleaner initialized."
        )

    # ======================================================
    # Helper Methods
    # ======================================================

    @staticmethod
    def normalize_text(value):

        """
        Normalize text values.

        Example

        ' finance '

        becomes

        'Finance'
        """

        if pd.isna(value):

            return DEFAULT_CATEGORICAL_VALUE

        return (
            str(value)
            .strip()
            .title()
        )

    @staticmethod
    def convert_boolean(value):
    if value is None:
        return None

    if isinstance(value, bool):
        return value

    value = str(value).strip().lower()

    if value in {"true", "t", "yes", "y", "1"}:
        return True

    if value in {"false", "f", "no", "n", "0"}:
        return False

    raise ValueError(
        f"Invalid boolean value: {value!r}. "
        "Expected true/false, yes/no, or 1/0."
        )

        if pd.isna(value):

            return DEFAULT_BOOLEAN_VALUE

        if isinstance(value, bool):

            return value

        value = (
            str(value)
            .strip()
            .lower()
        )

        if value in (
            "true",
            "yes",
            "1",
            "y",
        ):
            return True

        if value in (
            "false",
            "no",
            "0",
            "n",
        ):
            return False

        return DEFAULT_BOOLEAN_VALUE

    @staticmethod
    def cap_outliers(series):

        """
        Cap outliers using IQR.

        Returns
        -------
        cleaned_series,
        number_of_values_capped
        """

        q1 = series.quantile(0.25)

        q3 = series.quantile(0.75)

        iqr = q3 - q1

        lower = q1 - 1.5 * iqr

        upper = q3 + 1.5 * iqr

        capped = series.clip(
            lower=lower,
            upper=upper,
        )

        count = (
            (series != capped)
            .sum()
        )

        return capped, int(count)

    # ======================================================
    # Dataset Statistics
    # ======================================================

    def dataset_statistics(self):

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
    # Save Cleaning Report
    # ======================================================

    def save_quality_report(self):

        """
        Save quality report as JSON.
        """

        self.report["final_rows"] = len(
            self.df
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
            "Cleaning report saved."
            )
            # ======================================================
    # Remove Duplicate Records
    # ======================================================

    def remove_duplicates(self):
        """
        Remove duplicate incident records based on incident_id.
        """

        logger.info("Removing duplicate records...")

        before = len(self.df)

        self.df = self.df.drop_duplicates(
            subset=["incident_id"],
            keep="first",
        )

        removed = before - len(self.df)

        self.report["duplicates_removed"] = removed

        logger.info(
            "%d duplicate records removed.",
            removed,
        )

    # ======================================================
    # Handle Missing Values
    # ======================================================

    def handle_missing_values(self):
        """
        Fill missing values according to column type.
        """

        logger.info("Handling missing values...")

        missing_before = int(
            self.df.isna().sum().sum()
        )

        # Categorical Columns

        for column in CATEGORICAL_COLUMNS:

            if column in self.df.columns:

                self.df[column] = (
                    self.df[column]
                    .fillna(DEFAULT_CATEGORICAL_VALUE)
                    .apply(self.normalize_text)
                )

        # Numeric Columns

        for column in NUMERIC_COLUMNS:

            if column in self.df.columns:

                self.df[column] = pd.to_numeric(
                    self.df[column],
                    errors="coerce",
                )

                median_value = (
                    self.df[column]
                    .median()
                )

                if pd.isna(median_value):
                    median_value = DEFAULT_NUMERIC_VALUE

                self.df[column] = (
                    self.df[column]
                    .fillna(median_value)
                )

        # Boolean Columns

        for column in BOOLEAN_COLUMNS:

            if column in self.df.columns:

                self.df[column] = (
                    self.df[column]
                    .apply(self.convert_boolean)
                )

        missing_after = int(
            self.df.isna().sum().sum()
        )

        self.report["missing_values_filled"] = (
            missing_before - missing_after
        )

        logger.info(
            "Missing value handling completed."
        )

    # ======================================================
    # Parse Incident Date
    # ======================================================

    def parse_incident_date(self):
        """
        Convert incident_date to datetime format.
        """

        if "incident_date" not in self.df.columns:

            logger.warning(
                "incident_date column missing."
            )

            return

        logger.info(
            "Parsing incident_date..."
        )

        parsed_dates = pd.to_datetime(
    df["incident_date"],
    errors="coerce"
)

invalid_dates = (
    df["incident_date"].notna()
    & parsed_dates.isna()
)

if invalid_dates.any():
    count = int(invalid_dates.sum())
    raise ValueError(
        f"Found {count} invalid incident_date value(s)."
    )

df["incident_date"] = parsed_dates
        )

        invalid_dates = (
            self.df["incident_date"]
            .isna()
            .sum()
        )

        if invalid_dates > 0:

            logger.warning(
                "%d invalid dates detected.",
                invalid_dates,
            )

        logger.info(
            "Datetime conversion completed."
        )

    # ======================================================
    # Validate Numeric Columns
    # ======================================================

    def validate_numeric_columns(self):
        """
        Ensure numeric columns contain numeric values.
        """

        logger.info(
            "Validating numeric columns..."
        )

        for column in NUMERIC_COLUMNS:

            if column not in self.df.columns:
                continue

            self.df[column] = pd.to_numeric(
                self.df[column],
                errors="coerce",
            )

            self.df[column] = (
                self.df[column]
                .fillna(DEFAULT_NUMERIC_VALUE)
            )

        logger.info(
            "Numeric validation completed."
)
            # ======================================================
    # Standardize Categorical Columns
    # ======================================================

    def standardize_categories(self):
        """
        Standardize categorical columns by removing
        extra spaces and applying title case.
        """

        logger.info("Standardizing categorical columns...")

        for column in CATEGORICAL_COLUMNS:

            if column not in self.df.columns:
                continue

            self.df[column] = (
                self.df[column]
                .astype(str)
                .apply(self.normalize_text)
            )

        logger.info(
            "Categorical standardization completed."
        )

    # ======================================================
    # Normalize Boolean Columns
    # ======================================================

    def normalize_boolean_columns(self):
        """
        Normalize boolean columns.
        """

        logger.info(
            "Normalizing boolean columns..."
        )

        for column in BOOLEAN_COLUMNS:

            if column not in self.df.columns:
                continue

            self.df[column] = (
                self.df[column]
                .apply(self.convert_boolean)
                .astype(bool)
            )

        logger.info(
            "Boolean normalization completed."
        )

    # ======================================================
    # Range Validation
    # ======================================================

    def validate_ranges(self):
        """
        Validate important numeric ranges.
        """

        logger.info("Validating numeric ranges...")

        if "severity_score" in self.df.columns:

            self.df["severity_score"] = (
                self.df["severity_score"]
                .clip(lower=0, upper=10)
            )

        if "downtime_hours" in self.df.columns:

            self.df["downtime_hours"] = (
                self.df["downtime_hours"]
                .clip(lower=0)
            )

        if "detection_time_hours" in self.df.columns:

            self.df["detection_time_hours"] = (
                self.df["detection_time_hours"]
                .clip(lower=0)
            )

        if "response_team_size" in self.df.columns:

            self.df["response_team_size"] = (
                self.df["response_team_size"]
                .clip(lower=1)
            )

        if "records_affected" in self.df.columns:

            self.df["records_affected"] = (
                self.df["records_affected"]
                .clip(lower=0)
            )

        if "ransom_demand_usd" in self.df.columns:

            self.df["ransom_demand_usd"] = (
                self.df["ransom_demand_usd"]
                .clip(lower=0)
            )

        if "regulatory_fine_usd" in self.df.columns:

            self.df["regulatory_fine_usd"] = (
                self.df["regulatory_fine_usd"]
                .clip(lower=0)
            )

        logger.info(
            "Range validation completed."
        )

    # ======================================================
    # Handle Outliers
    # ======================================================

    def handle_outliers(self):
        """
        Cap outliers using IQR method.
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

            self.df[column] = cleaned_series

            total_outliers += capped

        self.report["outliers_capped"] = (
            total_outliers
        )

        logger.info(
            "%d outlier values capped.",
            total_outliers,
        )

    # ======================================================
    # Final Dataset Validation
    # ======================================================

    def final_validation(self):
        """
        Perform final validation before saving.
        """

        logger.info(
            "Running final validation..."
        )

        if self.df.empty:

            raise ValueError(
                "Dataset became empty after cleaning."
            )

        duplicate_count = (
            self.df["incident_id"]
            .duplicated()
            .sum()
        )

        if duplicate_count > 0:

            logger.warning(
                "%d duplicate incident IDs still exist.",
                duplicate_count,
            )

        missing_values = (
            self.df
            .isna()
            .sum()
            .sum()
        )

        logger.info(
            "Remaining missing values: %d",
            missing_values,
        )

        logger.info(
            "Final validation completed."
        )
            # ======================================================
    # Save Clean Dataset
    # ======================================================

    def save_clean_dataset(self):
        """
        Save cleaned dataset to processed directory.
        """

        logger.info("Saving cleaned dataset...")

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

    def run(self):
        """
        Execute the complete data cleaning pipeline.

        Returns
        -------
        pandas.DataFrame
            Cleaned dataframe.
        """

        logger.info("=" * 60)
        logger.info("Starting Data Cleaning Pipeline")
        logger.info("=" * 60)

        self.remove_duplicates()

        self.handle_missing_values()

        self.parse_incident_date()

        self.validate_numeric_columns()

        self.standardize_categories()

        self.normalize_boolean_columns()

        self.validate_ranges()

        self.handle_outliers()

        self.final_validation()

        self.dataset_statistics()

        self.save_quality_report()

        self.save_clean_dataset()

        logger.info("=" * 60)
        logger.info("Data Cleaning Pipeline Completed Successfully")
        logger.info("=" * 60)

        return self.df
        # ==========================================================
# Standalone Execution
# ==========================================================

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

        logger.exception(
            "Data Cleaning Pipeline Failed."
        )

        print("\nPipeline Error")
        print(error)
        
