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

logger = logging.getLogger(__name__)

if not logger.handlers:
    logging.basicConfig(
        filename=LOG_FILE,
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )


class DataLoader:
    """Load and validate the raw cybersecurity incident dataset."""

    def __init__(self, file_path=RAW_DATA_FILE):
        self.file_path = file_path

    def validate_file(self) -> None:
        """Validate that the configured dataset file exists."""
        if not self.file_path.exists():
            logger.error("Dataset file not found: %s", self.file_path)
            raise FileNotFoundError(f"Dataset not found:\n{self.file_path}")
        logger.info("Dataset file found: %s", self.file_path)

    def load_csv(self) -> pd.DataFrame:
        """Load the configured CSV into a DataFrame."""
        self.validate_file()
        try:
            df = pd.read_csv(
                self.file_path,
                encoding=CSV_ENCODING,
                sep=CSV_SEPARATOR,
            )
        except Exception as error:
            logger.exception("Unable to load dataset.")
            raise RuntimeError(f"Unable to load dataset: {error}") from error

        logger.info(
            "Dataset loaded successfully: %d rows, %d columns.",
            len(df),
            len(df.columns),
        )
        return df

    @staticmethod
    def validate_empty(df: pd.DataFrame) -> None:
        """Ensure the dataset contains at least one record."""
        if df.empty:
            raise ValueError("Dataset contains no records.")

    @staticmethod
    def validate_schema(df: pd.DataFrame) -> None:
        """Validate required columns and reject duplicate column names."""
        duplicated_columns = df.columns[df.columns.duplicated()].tolist()
        if duplicated_columns:
            raise ValueError(
                "Dataset contains duplicate column name(s): "
                f"{duplicated_columns}"
            )

        missing = sorted(set(EXPECTED_COLUMNS) - set(df.columns))
        if missing:
            raise ValueError(f"Missing required columns: {missing}")

    @staticmethod
    def validate_incident_ids(df: pd.DataFrame) -> None:
        """Validate that incident_id exists and contains no missing values."""
        if df["incident_id"].isna().any():
            raise ValueError("incident_id contains missing values.")

        duplicates = int(df["incident_id"].duplicated().sum())
        if duplicates > 0:
            # Duplicates are intentionally retained here for the cleaning stage
            # to remove deterministically; loading reports their presence.
            logger.warning("%d duplicate incident IDs found; cleaning will deduplicate.", duplicates)

    @staticmethod
    def dataset_summary(df: pd.DataFrame) -> None:
        """Print a concise dataset summary for local execution."""
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

    def run(self) -> pd.DataFrame:
        """Execute file, schema, and identifier validation and return raw data."""
        logger.info("=" * 60)
        logger.info("Starting Data Loader")
        logger.info("=" * 60)

        df = self.load_csv()
        self.validate_empty(df)
        self.validate_schema(df)
        self.validate_incident_ids(df)
        self.dataset_summary(df)

        logger.info("Data Loader completed successfully.")
        return df


if __name__ == "__main__":
    loader = DataLoader()
    dataframe = loader.run()
    print("\nFirst Five Records\n")
    print(dataframe.head())
