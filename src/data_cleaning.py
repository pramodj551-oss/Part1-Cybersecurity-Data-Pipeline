"""
data_cleaning.py

AI-Powered Cybersecurity Data Pipeline

Production-ready data cleaning module.

Author:
Pramod Prakash Jadhav
"""

from __future__ import annotations

import ipaddress
import json
import logging
from pathlib import Path
from typing import Dict

import pandas as pd

from config import (
    CLEAN_DATA_FILE,
    LOG_FILE,
    QUALITY_REPORT,
    VALID_SEVERITY,
)

# ---------------------------------------------------------------------
# Logging Configuration
# ---------------------------------------------------------------------

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger(__name__)


class DataCleaner:
    """
    Production-grade data cleaning pipeline.

    Responsibilities
    ----------------
    - Handle missing values
    - Remove duplicates
    - Normalize timestamps
    - Validate IP addresses
    - Standardize severity labels
    - Standardize attack types
    - Clean text fields
    - Generate quality report
    """

    def __init__(self, dataframe: pd.DataFrame):

        self.df = dataframe.copy()

        self.report: Dict[str, int] = {
            "initial_rows": len(dataframe),
            "initial_columns": len(dataframe.columns),
            "duplicates_removed": 0,
            "missing_values_filled": 0,
            "invalid_source_ips": 0,
            "invalid_destination_ips": 0,
            "final_rows": 0,
            "final_columns": 0,
        }

        logger.info("DataCleaner initialized.")

    # -------------------------------------------------------
    # Helper Methods
    # -------------------------------------------------------

    @staticmethod
    def _safe_strip(value):

        """
        Remove leading and trailing whitespace.

        Parameters
        ----------
        value : Any

        Returns
        -------
        Clean string
        """

        if pd.isna(value):
            return value

        return str(value).strip()

    @staticmethod
    def _normalize_case(value):

        """
        Convert text to Title Case.
        """

        if pd.isna(value):
            return value

        return str(value).strip().title()

    @staticmethod
    def _is_valid_ip(ip):

        """
        Validate IPv4/IPv6 address.
        """

        try:

            ipaddress.ip_address(str(ip))

            return True

        except Exception:

            return False

    @staticmethod
    def _safe_datetime(series):

        """
        Convert timestamps safely.
        """

        return pd.to_datetime(
            series,
            errors="coerce",
            utc=True,
        )

    # -------------------------------------------------------
    # Generic Utilities
    # -------------------------------------------------------

    def clean_column_names(self):

        """
        Standardize column names.

        Example

        Attack Type

        becomes

        attack_type
        """

        logger.info("Cleaning column names.")

        self.df.columns = (
            self.df.columns
            .str.strip()
            .str.lower()
            .str.replace(" ", "_")
        )

    def remove_empty_rows(self):

        """
        Remove rows where every value is missing.
        """

        before = len(self.df)

        self.df.dropna(
            how="all",
            inplace=True,
        )

        removed = before - len(self.df)

        logger.info(
            "%d completely empty rows removed.",
            removed,
        )

    def trim_text_columns(self):

        """
        Strip whitespace from all object columns.
        """

        object_columns = self.df.select_dtypes(
            include="object"
        ).columns

        for column in object_columns:

            self.df[column] = self.df[column].apply(
                self._safe_strip
            )

        logger.info(
            "Whitespace removed from text columns."
        )

    def convert_to_string(self):

        """
        Convert description column to string.
        """

        if "description" in self.df.columns:

            self.df["description"] = (
                self.df["description"]
                .fillna("")
                .astype(str)
            )

    def save_quality_report(self):

        """
        Save JSON quality report.
        """

        self.report["final_rows"] = len(self.df)

        self.report["final_columns"] = len(
            self.df.columns
        )

        report_path = Path(QUALITY_REPORT)

        report_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with open(
            report_path,
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                self.report,
                file,
                indent=4,
            )

        logger.info(
            "Quality report saved successfully."
  )
            # -------------------------------------------------------
    # Missing Value Handling
    # -------------------------------------------------------

    def handle_missing_values(self):
        """
        Handle missing values using column-specific rules.

        Rules
        -----
        - description -> ""
        - status -> "Unknown"
        - action -> "Unknown"
        - protocol -> "Unknown"
        - attack_type -> "Unknown"
        - country -> "Unknown"
        - device -> "Unknown"
        - severity -> "Medium"
        """

        logger.info("Handling missing values...")

        missing_before = int(self.df.isna().sum().sum())

        default_values = {
            "description": "",
            "status": "Unknown",
            "action": "Unknown",
            "protocol": "Unknown",
            "attack_type": "Unknown",
            "country": "Unknown",
            "device": "Unknown",
            "severity": "Medium",
        }

        for column, value in default_values.items():

            if column in self.df.columns:

                self.df[column] = self.df[column].fillna(value)

        if "incident_id" in self.df.columns:

            self.df.dropna(
                subset=["incident_id"],
                inplace=True,
            )

        if "timestamp" in self.df.columns:

            self.df.dropna(
                subset=["timestamp"],
                inplace=True,
            )

        missing_after = int(self.df.isna().sum().sum())

        filled = missing_before - missing_after

        self.report["missing_values_filled"] = filled

        logger.info(
            "Missing values handled. Filled: %d",
            filled,
        )

    # -------------------------------------------------------
    # Duplicate Removal
    # -------------------------------------------------------

    def remove_duplicates(self):
        """
        Remove duplicate rows.

        Priority:
        1. Duplicate incident_id
        2. Complete duplicate rows
        """

        logger.info("Removing duplicates...")

        before = len(self.df)

        if "incident_id" in self.df.columns:

            self.df.drop_duplicates(
                subset=["incident_id"],
                keep="first",
                inplace=True,
            )

        self.df.drop_duplicates(
            inplace=True,
        )

        removed = before - len(self.df)

        self.report["duplicates_removed"] = removed

        logger.info(
            "%d duplicate rows removed.",
            removed,
        )

    # -------------------------------------------------------
    # Timestamp Cleaning
    # -------------------------------------------------------

    def normalize_timestamp(self):
        """
        Convert timestamps into UTC datetime format.

        Invalid timestamps are removed.
        """

        if "timestamp" not in self.df.columns:

            logger.warning(
                "Timestamp column not found."
            )

            return

        logger.info("Normalizing timestamps...")

        self.df["timestamp"] = self._safe_datetime(
            self.df["timestamp"]
        )

        before = len(self.df)

        self.df.dropna(
            subset=["timestamp"],
            inplace=True,
        )

        removed = before - len(self.df)

        logger.info(
            "%d invalid timestamps removed.",
            removed,
        )

        self.df["year"] = self.df["timestamp"].dt.year

        self.df["month"] = self.df["timestamp"].dt.month

        self.df["day"] = self.df["timestamp"].dt.day

        self.df["hour"] = self.df["timestamp"].dt.hour

        logger.info(
            "Timestamp normalization completed."
        )

    # -------------------------------------------------------
    # Dataset Statistics
    # -------------------------------------------------------

    def dataset_statistics(self):
        """
        Log dataset statistics after cleaning.
        """

        logger.info("Generating cleaning statistics...")

        logger.info(
            "Rows: %d",
            len(self.df),
        )

        logger.info(
            "Columns: %d",
            len(self.df.columns),
        )

        logger.info(
            "Remaining Missing Values: %d",
            int(self.df.isna().sum().sum()),
        )

        print("\n" + "=" * 60)
        print("DATA CLEANING SUMMARY")
        print("=" * 60)

        print(f"Rows                : {len(self.df)}")
        print(f"Columns             : {len(self.df.columns)}")
        print(
            f"Duplicates Removed  : {self.report['duplicates_removed']}"
        )
        print(
            f"Missing Values Filled : {self.report['missing_values_filled']}"
        )
        print(
            f"Remaining Missing Values : {int(self.df.isna().sum().sum())}"
        )
        print("=" * 60)
            # -------------------------------------------------------
    # IP Address Validation
    # -------------------------------------------------------

    def validate_ip_addresses(self):
        """
        Validate source and destination IP addresses.

        Invalid IPs are replaced with 'Invalid_IP'
        and counted in the quality report.
        """

        logger.info("Validating IP addresses...")

        if "source_ip" in self.df.columns:

            invalid = ~self.df["source_ip"].apply(
                self._is_valid_ip
            )

            self.report["invalid_source_ips"] = int(
                invalid.sum()
            )

            self.df.loc[
                invalid,
                "source_ip",
            ] = "Invalid_IP"

        if "destination_ip" in self.df.columns:

            invalid = ~self.df["destination_ip"].apply(
                self._is_valid_ip
            )

            self.report["invalid_destination_ips"] = int(
                invalid.sum()
            )

            self.df.loc[
                invalid,
                "destination_ip",
            ] = "Invalid_IP"

        logger.info(
            "Source Invalid IPs: %d | Destination Invalid IPs: %d",
            self.report["invalid_source_ips"],
            self.report["invalid_destination_ips"],
        )

    # -------------------------------------------------------
    # Severity Standardization
    # -------------------------------------------------------

    def normalize_severity(self):
        """
        Standardize severity values.

        Examples
        --------
        HIGH -> High
        critical -> Critical
        MEDIUM -> Medium
        """

        if "severity" not in self.df.columns:
            return

        logger.info("Normalizing severity labels...")

        self.df["severity"] = (
            self.df["severity"]
            .astype(str)
            .str.strip()
            .str.title()
        )

        self.df.loc[
            ~self.df["severity"].isin(VALID_SEVERITY),
            "severity",
        ] = "Medium"

        logger.info("Severity normalization completed.")

    # -------------------------------------------------------
    # Attack Type Cleaning
    # -------------------------------------------------------

    def normalize_attack_type(self):
        """
        Normalize attack type names.
        """

        if "attack_type" not in self.df.columns:
            return

        logger.info("Cleaning attack type values...")

        self.df["attack_type"] = (
            self.df["attack_type"]
            .astype(str)
            .str.strip()
            .str.title()
        )

        replacements = {
            "Dos": "DoS",
            "Ddos": "DDoS",
            "Sql Injection": "SQL Injection",
            "Xss": "XSS",
            "Bruteforce": "Brute Force",
            "Ransomware Attack": "Ransomware",
            "Malware Attack": "Malware",
            "Phishing Attack": "Phishing",
        }

        self.df["attack_type"] = (
            self.df["attack_type"]
            .replace(replacements)
        )

        logger.info("Attack type normalization completed.")

    # -------------------------------------------------------
    # Country Cleaning
    # -------------------------------------------------------

    def clean_country(self):
        """
        Standardize country names.
        """

        if "country" not in self.df.columns:
            return

        logger.info("Cleaning country names...")

        self.df["country"] = (
            self.df["country"]
            .apply(self._normalize_case)
        )

        self.df["country"] = (
            self.df["country"]
            .replace(
                {
                    "Usa": "USA",
                    "Uae": "UAE",
                    "Uk": "UK",
                }
            )
        )

        logger.info("Country names standardized.")

    # -------------------------------------------------------
    # Generic Text Cleaning
    # -------------------------------------------------------

    def clean_text_columns(self):
        """
        Clean all object/string columns.
        """

        logger.info("Cleaning text columns...")

        text_columns = self.df.select_dtypes(
            include="object"
        ).columns

        for column in text_columns:

            self.df[column] = (
                self.df[column]
                .astype(str)
                .str.strip()
                .str.replace(
                    r"\s+",
                    " ",
                    regex=True,
                )
            )

        logger.info("Text normalization completed.")
            # -------------------------------------------------------
    # Save Clean Dataset
    # -------------------------------------------------------

    def save_clean_dataset(self):
        """
        Save cleaned dataset as CSV.
        """

        logger.info("Saving cleaned dataset...")

        output_path = Path(CLEAN_DATA_FILE)

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.df.to_csv(
            output_path,
            index=False,
        )

        logger.info(
            "Clean dataset saved successfully: %s",
            output_path,
        )

    # -------------------------------------------------------
    # Execute Complete Cleaning Pipeline
    # -------------------------------------------------------

    def run(self):
        """
        Execute the complete data cleaning pipeline.

        Returns
        -------
        pandas.DataFrame
            Cleaned dataframe
        """

        logger.info("=" * 60)
        logger.info("Starting Data Cleaning Pipeline")
        logger.info("=" * 60)

        self.clean_column_names()

        self.remove_empty_rows()

        self.trim_text_columns()

        self.convert_to_string()

        self.handle_missing_values()

        self.remove_duplicates()

        self.normalize_timestamp()

        self.validate_ip_addresses()

        self.normalize_severity()

        self.normalize_attack_type()

        self.clean_country()

        self.clean_text_columns()

        self.dataset_statistics()

        self.save_quality_report()

        self.save_clean_dataset()

        logger.info("=" * 60)
        logger.info("Data Cleaning Pipeline Completed Successfully")
        logger.info("=" * 60)

        return self.df


# ---------------------------------------------------------------------
# Standalone Execution
# ---------------------------------------------------------------------

if __name__ == "__main__":

    from data_loader import DataLoader

    try:

        logger.info("Loading raw dataset...")

        loader = DataLoader()

        raw_df = loader.run()

        logger.info("Running DataCleaner...")

        cleaner = DataCleaner(raw_df)

        clean_df = cleaner.run()

        print("\n" + "=" * 70)
        print("DATA CLEANING COMPLETED SUCCESSFULLY")
        print("=" * 70)
        print(f"Final Rows    : {len(clean_df)}")
        print(f"Final Columns : {len(clean_df.columns)}")
        print(f"Output File   : {CLEAN_DATA_FILE}")
        print(f"Quality Report: {QUALITY_REPORT}")
        print("=" * 70)

    except Exception as error:

        logger.exception("Pipeline failed.")

        print("\nERROR OCCURRED")
        print(error)
        
