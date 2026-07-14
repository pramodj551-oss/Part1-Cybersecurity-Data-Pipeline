"""
Pipeline Module

Master orchestration pipeline for the
Cybersecurity Incident Analytics Project.

Author:
Pramod Prakash Jadhav
"""

from __future__ import annotations

import logging
import time

import pandas as pd

from src.config import (
    ENGINEERED_DATA_FILE,
    LOG_FILE,
)
from src.data_loader import DataLoader
from src.data_cleaning import DataCleaner
from src.feature_engineering import FeatureEngineer
from src.database import DatabaseManager

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


# ==========================================================
# Analytics Pipeline
# ==========================================================

class AnalyticsPipeline:
    """
    End-to-End Analytics Pipeline.

    Pipeline Flow
    -------------

    Raw Dataset
        ↓
    Data Loader
        ↓
    Data Cleaning
        ↓
    Feature Engineering
        ↓
    SQLite Database
    """

    def __init__(self):

        self.raw_df = None

        self.clean_df = None

        self.engineered_df = None

        self.database_manager = DatabaseManager()

        self.start_time = None

        logger.info(
            "AnalyticsPipeline initialized."
        )

    # ======================================================
    # Load Raw Dataset
    # ======================================================

    def load_data(self):
        """
        Load raw dataset using DataLoader.
        """

        logger.info("=" * 60)
        logger.info("STEP 1 : DATA LOADING")
        logger.info("=" * 60)

        loader = DataLoader()

        self.raw_df = loader.run()

        logger.info(
            "Raw dataset loaded successfully."
        )

        logger.info(
            "Rows : %d | Columns : %d",
            len(self.raw_df),
            len(self.raw_df.columns),
        )

        return self.raw_df

    # ======================================================
    # Clean Dataset
    # ======================================================

    def clean_data(self):
        """
        Execute data cleaning pipeline.
        """

        logger.info("=" * 60)
        logger.info("STEP 2 : DATA CLEANING")
        logger.info("=" * 60)

        if self.raw_df is None:

            raise ValueError(
                "Raw dataset is not loaded."
            )

        cleaner = DataCleaner(
            self.raw_df
        )

        self.clean_df = cleaner.run()

        logger.info(
            "Data cleaning completed."
        )

        logger.info(
            "Rows : %d | Columns : %d",
            len(self.clean_df),
            len(self.clean_df.columns),
        )

        return self.clean_df
          # ======================================================
    # Feature Engineering
    # ======================================================

    def engineer_features(self):
        """
        Execute feature engineering pipeline.
        """

        logger.info("=" * 60)
        logger.info("STEP 3 : FEATURE ENGINEERING")
        logger.info("=" * 60)

        if self.clean_df is None:

            raise ValueError(
                "Clean dataset is not available."
            )

        engineer = FeatureEngineer(
            self.clean_df
        )

        self.engineered_df = engineer.run()

        logger.info(
            "Feature engineering completed."
        )

        logger.info(
            "Rows : %d | Columns : %d",
            len(self.engineered_df),
            len(self.engineered_df.columns),
        )

        return self.engineered_df

    # ======================================================
    # Save Engineered Dataset
    # ======================================================

    def save_engineered_dataset(self):
        """
        Save feature engineered dataset.
        """

        logger.info("=" * 60)
        logger.info("Saving engineered dataset...")
        logger.info("=" * 60)

        if self.engineered_df is None:

            raise ValueError(
                "Engineered dataset is not available."
            )

        self.engineered_df.to_csv(

            ENGINEERED_DATA_FILE,

            index=False,

        )

        logger.info(
            "Engineered dataset saved to %s",
            ENGINEERED_DATA_FILE,
        )

    # ======================================================
    # Store Dataset into SQLite
    # ======================================================

    def store_database(self):
        """
        Store engineered dataset
        into SQLite database.
        """

        logger.info("=" * 60)
        logger.info("STEP 4 : DATABASE STORAGE")
        logger.info("=" * 60)

        if self.engineered_df is None:

            raise ValueError(
                "Engineered dataset is not available."
            )

        manager = DatabaseManager()

        manager.connect()

        try:

            manager.replace_table(
                self.engineered_df
            )

            manager.verify_table()

            total_rows = (
                manager.get_row_count()
            )

            logger.info(
                "Database updated successfully."
            )

            logger.info(
                "Rows stored : %d",
                total_rows,
            )

        finally:

            manager.close()

    # ======================================================
    # Pipeline Validation
    # ======================================================

    def validate_pipeline(self):
        """
        Validate pipeline outputs.
        """

        logger.info(
            "Validating pipeline outputs..."
        )

        if self.raw_df is None:

            raise ValueError(
                "Raw dataset missing."
            )

        if self.clean_df is None:

            raise ValueError(
                "Clean dataset missing."
            )

        if self.engineered_df is None:

            raise ValueError(
                "Engineered dataset missing."
            )

        logger.info(
            "Pipeline validation successful."
      )
          # ======================================================
    # Generate Pipeline Summary
    # ======================================================

    def generate_summary(self):
        """
        Generate pipeline execution summary.
        """

        logger.info("=" * 60)
        logger.info("Generating Pipeline Summary")
        logger.info("=" * 60)

        summary = {

            "raw_records": len(self.raw_df),

            "clean_records": len(self.clean_df),

            "engineered_records": len(self.engineered_df),

            "original_features": len(
                self.raw_df.columns
            ),

            "engineered_features": len(
                self.engineered_df.columns
            ),

            "new_features_created": (

                len(self.engineered_df.columns)

                -

                len(self.raw_df.columns)

            )

        }

        return summary

    # ======================================================
    # Save Summary Report
    # ======================================================

    def save_summary(self):
        """
        Save pipeline summary as JSON.
        """

        import json

        summary = self.generate_summary()

        with open(

            SUMMARY_REPORT_FILE,

            "w",

            encoding="utf-8",

        ) as file:

            json.dump(

                summary,

                file,

                indent=4,

            )

        logger.info(
            "Summary report saved."
        )

    # ======================================================
    # Measure Pipeline Runtime
    # ======================================================

    def calculate_runtime(self):
        """
        Calculate total execution time.
        """

        runtime = (

            time.perf_counter()

            -

            self.start_time

        )

        logger.info(

            "Pipeline runtime : %.2f seconds",

            runtime,

        )

        return runtime

    # ======================================================
    # Display Statistics
    # ======================================================

    def display_statistics(self):
        """
        Print pipeline statistics.
        """

        runtime = self.calculate_runtime()

        print("\n")

        print("=" * 70)

        print("PIPELINE SUMMARY")

        print("=" * 70)

        print(

            f"Raw Records             : {len(self.raw_df)}"

        )

        print(

            f"Clean Records           : {len(self.clean_df)}"

        )

        print(

            f"Engineered Records      : {len(self.engineered_df)}"

        )

        print(

            f"Original Features       : {len(self.raw_df.columns)}"

        )

        print(

            f"Engineered Features     : {len(self.engineered_df.columns)}"

        )

        print(

            f"Execution Time (sec)    : {runtime:.2f}"

        )

        print("=" * 70)

    # ======================================================
    # Pipeline Health Check
    # ======================================================

    def health_check(self):
        """
        Perform basic health checks.
        """

        logger.info(
            "Performing pipeline health check..."
        )

        if self.engineered_df.empty:

            raise ValueError(
                "Engineered dataset is empty."
            )

        if self.engineered_df.isna().sum().sum() > 0:

            logger.warning(
                "Engineered dataset contains missing values."
            )

        logger.info(
            "Pipeline health check completed."
      )
          # ======================================================
    # Execute Complete Analytics Pipeline
    # ======================================================

    def run(self):
        """
        Execute the complete analytics pipeline.

        Pipeline Flow
        -------------
        1. Load Data
        2. Clean Data
        3. Feature Engineering
        4. Save Engineered Dataset
        5. Store in SQLite
        6. Validate Outputs
        7. Health Check
        8. Save Summary
        """

        self.start_time = time.perf_counter()

        logger.info("=" * 70)
        logger.info("STARTING ANALYTICS PIPELINE")
        logger.info("=" * 70)

        try:

            self.load_data()

            self.clean_data()

            self.engineer_features()

            self.save_engineered_dataset()

            self.store_database()

            self.validate_pipeline()

            self.health_check()

            self.save_summary()

            self.display_statistics()

            logger.info("=" * 70)
            logger.info("PIPELINE EXECUTED SUCCESSFULLY")
            logger.info("=" * 70)

            return self.engineered_df

        except Exception as error:

            logger.exception(
                "Pipeline execution failed."
            )

            raise error
          # ==========================================================
# Standalone Execution
# ==========================================================

if __name__ == "__main__":

    try:

        pipeline = AnalyticsPipeline()

        dataframe = pipeline.run()

        print("\n")
        print("=" * 70)
        print("CYBERSECURITY ANALYTICS PIPELINE COMPLETED")
        print("=" * 70)

        print(
            f"Final Records  : {len(dataframe)}"
        )

        print(
            f"Final Features : {len(dataframe.columns)}"
        )

        print(
            "Status         : SUCCESS"
        )

        print("=" * 70)

    except Exception as error:

        logger.exception(
            "Fatal pipeline error."
        )

        print("\nPipeline Failed")
        print(error)
      
