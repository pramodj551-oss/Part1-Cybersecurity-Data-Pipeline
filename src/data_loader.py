"""
Data Loader Module

Loads and validates the raw cybersecurity incident dataset.

Author: Pramod Prakash Jadhav
"""

from __future__ import annotations

import logging

import pandas as pd

from src.config import (
    CSV_ENCODING,
    CSV_SEPARATOR,
    EXPECTED_COLUMNS,
    LOG_FILE,
    RAW_DATA_FILE,
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


class DataLoader:
    """
    Loads and validates the cybersecurity incident dataset.
    """

    def __init__(self, file_path=RAW_DATA_FILE):

        self.file_path = file_path

    # ======================================================
    # File Validation
    # ======================================================

    def validate_file(self):

        """
        Validate dataset file existence.
        """

        if not self.file_path.exists():

            logger.error("Dataset file not found.")

            raise FileNotFoundError(
                f"Dataset not found:\n{self.file_path}"
            )

        logger.info("Dataset file found.")

    # ======================================================
    # Load CSV
    # ======================================================

    def load_csv(self):

        """
        Load CSV into DataFrame.
        """

        self.validate_file()

        try:

            df = pd.read_csv(
                self.file_path,
                encoding=CSV_ENCODING,
                sep=CSV_SEPARATOR,
            )

            logger.info(
                "Dataset loaded successfully."
            )

            return df

        except Exception as error:

            logger.exception(
                "Unable to load dataset."
            )

            raise error

    # ======================================================
    # Empty Dataset Validation
    # ======================================================

    @staticmethod
    def validate_empty(df):

        """
        Ensure dataset is not empty.
        """

        if df.empty:

            raise ValueError(
                "Dataset contains no records."
            )

    # ======================================================
    # Schema Validation
    # ======================================================

    @staticmethod
    def validate_schema(df):

        """
        Validate expected columns.
        """

        missing = sorted(
            list(
                set(EXPECTED_COLUMNS)
                - set(df.columns)
            )
        )

        if missing:

            raise ValueError(
                f"Missing Columns:\n{missing}"
            )

    # ======================================================
    # Duplicate Incident ID Validation
    # ======================================================

    @staticmethod
    def validate_incident_ids(df):

        """
        Check duplicate incident IDs.
        """

        duplicates = (
            df["incident_id"]
            .duplicated()
            .sum()
        )

        if duplicates > 0:

            logger.warning(
                "%d duplicate incident IDs found.",
                duplicates,
            )

    # ======================================================
    # Dataset Summary
    # ======================================================

    @staticmethod
    def dataset_summary(df):

        """
        Print dataset summary.
        """

        print("\n" + "=" * 60)
        print("CYBERSECURITY INCIDENT DATASET")
        print("=" * 60)

        print(f"Rows    : {df.shape[0]}")
        print(f"Columns : {df.shape[1]}")

        print("\nColumn Names")

        for column in df.columns:

            print(f"• {column}")

        print("\nData Types")

        print(df.dtypes)

        print("\nMissing Values")

        print(df.isnull().sum())

        print("=" * 60)

    # ======================================================
    # Run Complete Loader
    # ======================================================

    def run(self):

        """
        Execute loading pipeline.
        """

        logger.info("=" * 60)
        logger.info("Starting Data Loader")
        logger.info("=" * 60)

        df = self.load_csv()

        self.validate_empty(df)

        self.validate_schema(df)

        self.validate_incident_ids(df)

        self.dataset_summary(df)

        logger.info(
            "Data Loader completed successfully."
        )

        return df


# ==========================================================
# Standalone Execution
# ==========================================================

if __name__ == "__main__":

    loader = DataLoader()

    dataframe = loader.run()

    print("\nFirst Five Records\n")

    print(dataframe.head())
