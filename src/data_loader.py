"""
Loads and validates cybersecurity dataset.

Author:
Pramod Prakash Jadhav
"""

import logging
from pathlib import Path

import pandas as pd

from config import (
    RAW_DATA_FILE,
    EXPECTED_COLUMNS,
    LOG_FILE,
)

# ---------------------------------------------------
# Logger Configuration
# ---------------------------------------------------

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------
# Data Loader Class
# ---------------------------------------------------

class DataLoader:

    """
    Load raw CSV dataset.

    Performs:
        - File validation
        - Empty file validation
        - Column validation
    """

    def __init__(self, file_path: Path = RAW_DATA_FILE):

        self.file_path = file_path

    def validate_file(self):

        """
        Validate input file exists.
        """

        if not self.file_path.exists():
            logger.error("Dataset not found.")

            raise FileNotFoundError(
                f"Dataset not found:\n{self.file_path}"
            )

    def load_csv(self):

        """
        Load CSV file.

        Returns
        -------
        pandas.DataFrame
        """

        self.validate_file()

        logger.info("Loading dataset...")

        df = pd.read_csv(self.file_path)

        logger.info("Dataset loaded successfully.")

        return df

    def validate_columns(self, df):

        """
        Check whether expected columns exist.
        """

        missing = list(
            set(EXPECTED_COLUMNS) -
            set(df.columns)
        )

        if missing:

            logger.error(
                f"Missing columns: {missing}"
            )

            raise ValueError(
                f"Dataset missing columns:\n{missing}"
            )

        logger.info("Column validation passed.")

    def summary(self, df):

        """
        Print dataset summary.
        """

        logger.info("Generating dataset summary.")

        print("=" * 50)

        print("DATASET SUMMARY")

        print("=" * 50)

        print(f"Rows      : {len(df)}")

        print(f"Columns   : {len(df.columns)}")

        print()

        print(df.info())

        print()

        print(df.head())

    def run(self):

        """
        Complete loading pipeline.
        """

        df = self.load_csv()

        self.validate_columns(df)

        self.summary(df)

        logger.info("Data Loader completed successfully.")

        return df


# ---------------------------------------------------
# Main
# ---------------------------------------------------

if __name__ == "__main__":

    loader = DataLoader()

    dataframe = loader.run()
