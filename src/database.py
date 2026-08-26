"""
Database Module

Stores the feature engineered cybersecurity incident dataset into SQLite.

Author:
Pramod Prakash Jadhav
"""

from __future__ import annotations

import logging
import sqlite3
from pathlib import Path

import pandas as pd

from src.config import (
    DATABASE_FILE,
    DATABASE_TABLE,
    ENGINEERED_DATA_FILE,
    EXPECTED_COLUMNS,
    LOG_FILE,
    OUTPUT_DIR,
)


logger = logging.getLogger(__name__)

if not logger.handlers:
    logging.basicConfig(
        filename=LOG_FILE,
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )


class DatabaseManager:
    """Production-grade SQLite database manager."""

    def __init__(self, database_path=DATABASE_FILE):
        self.database_path = Path(database_path)
        self.connection: sqlite3.Connection | None = None
        self.cursor: sqlite3.Cursor | None = None
        logger.info("DatabaseManager initialized.")

    def connect(self) -> None:
        """Establish SQLite connection."""
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            self.connection = sqlite3.connect(str(self.database_path))
            self.cursor = self.connection.cursor()
            logger.info("Database connection established.")
        except sqlite3.Error:
            logger.exception("Database connection failed.")
            raise

    def validate_connection(self) -> None:
        """Ensure database connection exists."""
        if self.connection is None or self.cursor is None:
            raise ConnectionError("Database connection is not established.")

    @staticmethod
    def load_engineered_dataset() -> pd.DataFrame:
        """Load and validate the engineered dataset."""
        if not ENGINEERED_DATA_FILE.exists():
            raise FileNotFoundError(
                f"Engineered dataset not found: {ENGINEERED_DATA_FILE}"
            )

        dataframe = pd.read_csv(
            ENGINEERED_DATA_FILE,
            parse_dates=["incident_date"],
        )

        if dataframe.empty:
            raise ValueError("Engineered dataset is empty.")

        missing_columns = [
            column for column in EXPECTED_COLUMNS
            if column not in dataframe.columns
        ]
        if missing_columns:
            raise ValueError(
                f"Engineered dataset is missing required columns: {missing_columns}"
            )

        duplicate_ids = int(dataframe["incident_id"].duplicated().sum())
        if duplicate_ids:
            raise ValueError(
                f"Engineered dataset contains {duplicate_ids} duplicate incident_id value(s)."
            )

        if dataframe["incident_id"].isna().any():
            raise ValueError("Engineered dataset contains missing incident_id values.")

        logger.info("Engineered dataset loaded and validated: %d rows.", len(dataframe))
        return dataframe

    def database_info(self) -> None:
        """Display database information."""
        self.validate_connection()
        print("\n" + "=" * 60)
        print("DATABASE INFORMATION")
        print("=" * 60)
        print(f"Database : {self.database_path}")
        print(f"Table    : {DATABASE_TABLE}")
        print("=" * 60)

    def create_table(self) -> None:
        """Create the controlled SQLite schema if it does not exist."""
        self.validate_connection()
        create_table_query = f"""
        CREATE TABLE IF NOT EXISTS {DATABASE_TABLE} (
            incident_id TEXT PRIMARY KEY,
            incident_date TIMESTAMP,
            sector TEXT,
            region TEXT,
            attack_type TEXT,
            threat_actor TEXT,
            records_affected REAL,
            downtime_hours REAL,
            ransom_demand_usd REAL,
            detection_time_hours REAL,
            severity_score REAL,
            response_team_size REAL,
            regulatory_fine_usd REAL,
            resolved_within_7_days INTEGER,
            data_exfiltration INTEGER,
            zero_day_used INTEGER
        );
        """
        try:
            self.cursor.execute(create_table_query)
            self.connection.commit()
            logger.info("Database table verified/created successfully.")
        except sqlite3.Error:
            self.connection.rollback()
            logger.exception("Table creation failed.")
            raise

    def insert_dataframe(
        self,
        dataframe: pd.DataFrame,
        if_exists: str = "append",
    ) -> None:
        """Insert a validated dataframe without silently changing schema."""
        self.validate_connection()
        if dataframe.empty:
            raise ValueError("Cannot insert empty dataframe.")
        if if_exists not in {"append", "fail"}:
            raise ValueError(
                "if_exists must be 'append' or 'fail'; use replace_table() for refreshes."
            )

        try:
            dataframe.to_sql(
                DATABASE_TABLE,
                self.connection,
                if_exists=if_exists,
                index=False,
                method="multi",
            )
            self.connection.commit()
            logger.info("%d rows inserted.", len(dataframe))
        except Exception:
            self.connection.rollback()
            logger.exception("Data insertion failed.")
            raise

    def replace_table(self, dataframe: pd.DataFrame) -> None:
        """Refresh table data while preserving the controlled SQLite schema."""
        self.validate_connection()
        if dataframe.empty:
            raise ValueError("Cannot replace table with an empty dataframe.")

        try:
            self.cursor.execute(f"DELETE FROM {DATABASE_TABLE}")
            self.connection.commit()
            self.insert_dataframe(dataframe, if_exists="append")
            logger.info("Database table refreshed while preserving schema.")
        except Exception:
            self.connection.rollback()
            logger.exception("Table refresh failed.")
            raise

    def append_table(self, dataframe: pd.DataFrame) -> None:
        """Append new records to the existing table."""
        self.insert_dataframe(dataframe, if_exists="append")

    def verify_table(self) -> None:
        """Verify table existence and required schema."""
        self.validate_connection()
        table = self.cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
            (DATABASE_TABLE,),
        ).fetchone()
        if table is None:
            raise ValueError("Database table not found.")

        schema = self.get_table_schema()
        actual_columns = set(schema["name"].tolist())
        missing_columns = [
            column for column in EXPECTED_COLUMNS
            if column not in actual_columns
        ]
        if missing_columns:
            raise ValueError(
                f"Database table is missing required columns: {missing_columns}"
            )

        incident_pk = schema.loc[schema["name"] == "incident_id", "pk"]
        if incident_pk.empty or int(incident_pk.iloc[0]) != 1:
            raise ValueError("incident_id must remain the SQLite PRIMARY KEY.")

        logger.info("Table and schema verification successful.")

    def execute_query(self, query: str, parameters: tuple = ()) -> None:
        """Execute a non-SELECT SQL statement safely with parameters."""
        self.validate_connection()
        try:
            self.cursor.execute(query, parameters)
            self.connection.commit()
            logger.info("SQL query executed successfully.")
        except sqlite3.Error:
            self.connection.rollback()
            logger.exception("SQL query execution failed.")
            raise

    def fetch_dataframe(
        self,
        query: str,
        parameters: tuple = (),
    ) -> pd.DataFrame:
        """Execute a SELECT query and return a dataframe."""
        self.validate_connection()
        try:
            dataframe = pd.read_sql_query(
                query,
                self.connection,
                params=parameters,
            )
            logger.info("%d rows fetched.", len(dataframe))
            return dataframe
        except sqlite3.Error:
            logger.exception("Data fetch failed.")
            raise

    def get_row_count(self) -> int:
        """Return total row count."""
        self.validate_connection()
        result = self.cursor.execute(
            f"SELECT COUNT(*) FROM {DATABASE_TABLE}"
        ).fetchone()
        return int(result[0])

    def get_table_schema(self) -> pd.DataFrame:
        """Return SQLite table schema."""
        self.validate_connection()
        return pd.read_sql_query(
            f"PRAGMA table_info({DATABASE_TABLE})",
            self.connection,
        )

    def export_query_results(self, query: str, output_file=None) -> None:
        """Export query results to CSV."""
        if output_file is None:
            output_file = OUTPUT_DIR / "query_results.csv"
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        dataframe = self.fetch_dataframe(query)
        dataframe.to_csv(output_path, index=False)
        logger.info("Query results exported to %s", output_path)

    def preview_table(self, rows: int = 5) -> pd.DataFrame:
        """Return first N rows from the table."""
        if rows < 1:
            raise ValueError("rows must be at least 1.")
        return self.fetch_dataframe(
            f"SELECT * FROM {DATABASE_TABLE} LIMIT ?",
            (rows,),
        )

    def close(self) -> None:
        """Close SQLite connection safely."""
        if self.connection is not None:
            self.connection.close()
            self.connection = None
            self.cursor = None
            logger.info("Database connection closed.")

    def run(self) -> pd.DataFrame:
        """Execute complete database pipeline."""
        logger.info("Starting Database Pipeline")
        try:
            self.connect()
            dataframe = self.load_engineered_dataset()
            self.create_table()
            self.replace_table(dataframe)
            self.verify_table()

            row_count = self.get_row_count()
            if row_count != len(dataframe):
                raise ValueError(
                    f"Database row-count mismatch: expected {len(dataframe)}, got {row_count}."
                )

            self.database_info()
            logger.info(
                "Database Pipeline completed successfully: %d rows.",
                row_count,
            )
            return dataframe
        except Exception:
            logger.exception("Database Pipeline failed.")
            raise
        finally:
            self.close()


if __name__ == "__main__":
    try:
        manager = DatabaseManager()
        dataframe = manager.run()
        print("\n" + "=" * 70)
        print("DATABASE PIPELINE COMPLETED")
        print("=" * 70)
        print(f"Rows Inserted : {len(dataframe)}")
        print(f"Database File : {DATABASE_FILE}")
        print(f"Table Name    : {DATABASE_TABLE}")
        print("=" * 70)
    except Exception as error:
        print("\nDatabase Error")
        print(error)
