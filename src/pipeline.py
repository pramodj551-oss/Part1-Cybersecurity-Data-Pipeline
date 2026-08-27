"""Master orchestration pipeline for Cybersecurity Incident Analytics."""

from __future__ import annotations

import time

import numpy as np
import pandas as pd

from src.config import ENGINEERED_DATA_FILE, EXPECTED_COLUMNS, SUMMARY_REPORT_FILE
from src.data_cleaning import DataCleaner
from src.data_loader import DataLoader
from src.database import DatabaseManager
from src.feature_engineering import FeatureEngineer
from src.logger import logger


class AnalyticsPipeline:
    """Execute and validate the complete analytics pipeline."""

    def __init__(self) -> None:
        self.raw_df: pd.DataFrame | None = None
        self.clean_df: pd.DataFrame | None = None
        self.engineered_df: pd.DataFrame | None = None
        self.database_manager = DatabaseManager()
        self.start_time: float | None = None

    def load_data(self) -> pd.DataFrame:
        logger.info("STEP 1 : DATA LOADING")
        self.raw_df = DataLoader().run()
        if self.raw_df.empty:
            raise ValueError("Raw dataset is empty.")
        logger.info("Raw dataset: %d rows, %d columns", len(self.raw_df), len(self.raw_df.columns))
        return self.raw_df

    def clean_data(self) -> pd.DataFrame:
        logger.info("STEP 2 : DATA CLEANING")
        if self.raw_df is None:
            raise ValueError("Raw dataset is not loaded.")
        self.clean_df = DataCleaner(self.raw_df).run()
        if self.clean_df.empty:
            raise ValueError("Clean dataset is empty.")
        return self.clean_df

    def engineer_features(self) -> pd.DataFrame:
        logger.info("STEP 3 : FEATURE ENGINEERING")
        if self.clean_df is None:
            raise ValueError("Clean dataset is not available.")
        self.engineered_df = FeatureEngineer(self.clean_df).run()
        if self.engineered_df.empty:
            raise ValueError("Engineered dataset is empty.")
        return self.engineered_df

    def save_engineered_dataset(self) -> None:
        logger.info("Saving engineered dataset...")
        if self.engineered_df is None:
            raise ValueError("Engineered dataset is not available.")
        ENGINEERED_DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
        self.engineered_df.to_csv(ENGINEERED_DATA_FILE, index=False)
        self._validate_saved_engineered_dataset()
        logger.info("Engineered dataset saved to %s", ENGINEERED_DATA_FILE)

    def _validate_saved_engineered_dataset(self) -> None:
        """Validate the persisted engineered CSV, not only the in-memory dataframe."""
        if not ENGINEERED_DATA_FILE.exists():
            raise IOError(f"Failed to create {ENGINEERED_DATA_FILE}")
        if ENGINEERED_DATA_FILE.stat().st_size == 0:
            raise IOError(f"Engineered dataset is empty on disk: {ENGINEERED_DATA_FILE}")
        saved_df = pd.read_csv(ENGINEERED_DATA_FILE)
        if saved_df.empty:
            raise ValueError("Persisted engineered dataset contains no rows.")
        missing = [column for column in EXPECTED_COLUMNS if column not in saved_df.columns]
        if missing:
            raise ValueError(f"Persisted engineered dataset is missing required columns: {missing}")
        if self.engineered_df is not None and len(saved_df) != len(self.engineered_df):
            raise ValueError(
                f"Persisted engineered row-count mismatch: expected {len(self.engineered_df)}, got {len(saved_df)}."
            )
        if saved_df["incident_id"].isna().any() or saved_df["incident_id"].duplicated().any():
            raise ValueError("Persisted engineered dataset has invalid incident_id values.")
        if saved_df.isna().any().any():
            raise ValueError("Persisted engineered dataset contains missing values.")

        numeric = saved_df.select_dtypes(include=[np.number])
        if not numeric.empty and not np.isfinite(numeric.to_numpy()).all():
            raise ValueError(
                "Persisted engineered dataset contains non-finite numeric values."
            )

    def store_database(self) -> int:
        logger.info("STEP 4 : DATABASE STORAGE")
        if self.engineered_df is None:
            raise ValueError("Engineered dataset is not available.")

        manager = self.database_manager
        manager.connect()
        try:
            manager.create_table(self.engineered_df)
            manager.verify_dataframe_schema(self.engineered_df)
            manager.replace_table(self.engineered_df)
            manager.verify_table()
            manager.verify_dataframe_schema(self.engineered_df)

            row_count = manager.get_row_count()
            if row_count != len(self.engineered_df):
                raise ValueError(
                    f"Database row-count mismatch: expected {len(self.engineered_df)}, got {row_count}."
                )

            logger.info("Database updated successfully: %d rows", row_count)
            return row_count
        except Exception:
            logger.exception("Database storage stage failed.")
            raise
        finally:
            manager.close()

    def validate_pipeline(self, database_rows: int | None = None) -> None:
        logger.info("Validating pipeline outputs...")
        if self.raw_df is None or self.clean_df is None or self.engineered_df is None:
            raise ValueError("One or more pipeline datasets are missing.")

        if len(self.clean_df) > len(self.raw_df):
            raise ValueError("Cleaning stage increased row count unexpectedly.")
        if len(self.engineered_df) != len(self.clean_df):
            raise ValueError("Feature engineering changed row count unexpectedly.")

        if self.engineered_df["incident_id"].isna().any():
            raise ValueError("Engineered dataset contains missing incident_id values.")
        if self.engineered_df["incident_id"].duplicated().any():
            raise ValueError("Engineered dataset contains duplicate incident_id values.")
        if self.engineered_df.isna().any().any():
            raise ValueError("Engineered dataset contains missing values.")

        if database_rows is not None and database_rows != len(self.engineered_df):
            raise ValueError(
                f"Database/output row-count mismatch: expected {len(self.engineered_df)}, got {database_rows}."
            )

        self._validate_saved_engineered_dataset()
        logger.info("Pipeline validation successful.")

    def generate_summary(self, database_rows: int | None = None) -> dict[str, object]:
        if self.raw_df is None or self.clean_df is None or self.engineered_df is None:
            raise ValueError("Pipeline outputs are not available.")
        return {
            "status": "SUCCESS",
            "raw_records": len(self.raw_df),
            "clean_records": len(self.clean_df),
            "engineered_records": len(self.engineered_df),
            "database_records": database_rows,
            "original_features": len(self.raw_df.columns),
            "engineered_features": len(self.engineered_df.columns),
            "new_features_created": max(0, len(self.engineered_df.columns) - len(self.raw_df.columns)),
        }

    def save_summary(self, database_rows: int | None = None) -> dict[str, object]:
        """Save and verify the configured summary report as CSV."""
        summary = self.generate_summary(database_rows)
        SUMMARY_REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
        pd.DataFrame([summary]).to_csv(SUMMARY_REPORT_FILE, index=False)
        if not SUMMARY_REPORT_FILE.exists() or SUMMARY_REPORT_FILE.stat().st_size == 0:
            raise IOError(f"Failed to create {SUMMARY_REPORT_FILE}")
        persisted_summary = pd.read_csv(SUMMARY_REPORT_FILE)
        if persisted_summary.empty or persisted_summary.iloc[0]["status"] != "SUCCESS":
            raise ValueError("Persisted summary report is invalid.")
        logger.info("Summary report saved to %s", SUMMARY_REPORT_FILE)
        return summary

    def calculate_runtime(self) -> float:
        if self.start_time is None:
            raise RuntimeError("Pipeline timer was not started.")
        return time.perf_counter() - self.start_time

    def display_statistics(self) -> None:
        if self.raw_df is None or self.clean_df is None or self.engineered_df is None:
            return
        print("\n" + "=" * 70)
        print("PIPELINE SUMMARY")
        print("=" * 70)
        print(f"Raw Records             : {len(self.raw_df)}")
        print(f"Clean Records           : {len(self.clean_df)}")
        print(f"Engineered Records      : {len(self.engineered_df)}")
        print(f"Original Features       : {len(self.raw_df.columns)}")
        print(f"Engineered Features     : {len(self.engineered_df.columns)}")
        print(f"Execution Time (sec)    : {self.calculate_runtime():.2f}")
        print("=" * 70)

    def health_check(self) -> None:
        """Fail fast on invalid final output instead of only warning."""
        if self.engineered_df is None or self.engineered_df.empty:
            raise ValueError("Engineered dataset is empty.")
        if self.engineered_df.isna().any().any():
            raise ValueError("Engineered dataset contains missing values.")
        logger.info("Pipeline health check passed.")

    def run(self) -> pd.DataFrame:
        self.start_time = time.perf_counter()
        logger.info("STARTING ANALYTICS PIPELINE")
        try:
            self.load_data()
            self.clean_data()
            self.engineer_features()
            self.save_engineered_dataset()
            database_rows = self.store_database()
            self.validate_pipeline(database_rows)
            self.health_check()
            self.save_summary(database_rows)
            self.display_statistics()
            logger.info("PIPELINE EXECUTED SUCCESSFULLY")
            return self.engineered_df
        except Exception:
            logger.exception("Pipeline execution failed.")
            raise


if __name__ == "__main__":
    try:
        dataframe = AnalyticsPipeline().run()
        print("\n" + "=" * 70)
        print("CYBERSECURITY ANALYTICS PIPELINE COMPLETED")
        print("=" * 70)
        print(f"Final Records  : {len(dataframe)}")
        print(f"Final Features : {len(dataframe.columns)}")
        print("Status         : SUCCESS")
        print("=" * 70)
    except Exception as error:
        logger.exception("Fatal pipeline error.")
        print("\nPipeline Failed")
        print(error)
        raise
