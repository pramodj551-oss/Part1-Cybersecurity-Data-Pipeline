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
