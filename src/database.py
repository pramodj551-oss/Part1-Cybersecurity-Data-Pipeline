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
    BOOLEAN_COLUMNS,
    DATABASE_FILE,
    DATABASE_TABLE,
    ENGINEERED_DATA_FILE,
    EXPECTED_COLUMNS,
    LOG_FILE,
    NUMERIC_COLUMNS,
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

    def connect(self) -> None:
        """Establish SQLite connection."""
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            self.connection = sqlite3.connect(str(self.database_path))
            self.cursor = self.connection.cursor()
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

        dataframe = pd.read_csv(ENGINEERED_DATA_FILE, parse_dates=["incident_date"])

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

        if dataframe.isna().any().any():
            missing = dataframe.columns[dataframe.isna().any()].tolist()
            raise ValueError(f"Engineered dataset contains missing values: {missing}")

        return dataframe

    @staticmethod
    def _sqlite_type(series: pd.Series) -> str:
        """Map a pandas series to a safe SQLite storage type."""
        if pd.api.types.is_bool_dtype(series):
            return "INTEGER"
        if pd.api.types.is_integer_dtype(series):
            return "INTEGER"
        if pd.api.types.is_float_dtype(series):
            return "REAL"
        if pd.api.types.is_datetime64_any_dtype(series):
            return "TIMESTAMP"
        return "TEXT"

    @staticmethod
    def _quote_identifier(identifier: str) -> str:
        """Quote a SQLite identifier safely."""
        return '"' + str(identifier).replace('"', '""') + '"'

    def create_table(self, dataframe: pd.DataFrame | None = None) -> None:
        """Create the controlled SQLite schema and add new engineered columns."""
        self.validate_connection()
        columns = dataframe.columns.tolist() if dataframe is not None else EXPECTED_COLUMNS.copy()
        if not columns:
            raise ValueError("Cannot create database schema without columns.")

        definitions: list[str] = []
        for column in columns:
            if column == "incident_id":
                definitions.append('"incident_id" TEXT PRIMARY KEY')
                continue
            if dataframe is not None and column in dataframe.columns:
                sqlite_type = self._sqlite_type(dataframe[column])
            elif column in BOOLEAN_COLUMNS:
                sqlite_type = "INTEGER"
            elif column in NUMERIC_COLUMNS:
                sqlite_type = "REAL"
            elif column == "incident_date":
                sqlite_type = "TIMESTAMP"
            else:
                sqlite_type = "TEXT"
            definitions.append(f"{self._quote_identifier(column)} {sqlite_type}")

        query = (
            f"CREATE TABLE IF NOT EXISTS {self._quote_identifier(DATABASE_TABLE)} ("
            + ", ".join(definitions) + ");"
        )

        try:
            self.cursor.execute(query)
            existing = self.get_table_schema()
            existing_columns = set(existing["name"].tolist())
            if dataframe is not None:
                for column in columns:
                    if column in existing_columns:
                        continue
                    if column == "incident_id":
                        raise ValueError(
                            "Existing database table is missing the incident_id PRIMARY KEY."
                        )
                    sqlite_type = self._sqlite_type(dataframe[column])
                    self.cursor.execute(
                        f"ALTER TABLE {self._quote_identifier(DATABASE_TABLE)} "
                        f"ADD COLUMN {self._quote_identifier(column)} {sqlite_type}"
                    )
            self.connection.commit()
        except Exception:
            self.connection.rollback()
            logger.exception("Table creation/schema migration failed.")
            raise

    def verify_dataframe_schema(self, dataframe: pd.DataFrame) -> None:
        """Verify dataframe columns are represented in the database schema."""
        self.validate_connection()
        schema = self.get_table_schema()
        database_columns = schema["name"].tolist()
        missing = [column for column in dataframe.columns if column not in database_columns]
        if missing:
            raise ValueError(f"Database is missing engineered columns: {missing}")

    def insert_dataframe(self, dataframe: pd.DataFrame, if_exists: str = "append") -> None:
        """Insert validated dataframe rows."""
        self.validate_connection()
        if dataframe.empty:
            raise ValueError("Cannot insert empty dataframe.")
        if if_exists not in {"append", "fail"}:
            raise ValueError("if_exists must be 'append' or 'fail'.")
        self.verify_dataframe_schema(dataframe)
        try:
            dataframe.to_sql(
                DATABASE_TABLE,
                self.connection,
                if_exists=if_exists,
                index=False,
                method="multi",
            )
            self.connection.commit()
        except Exception:
            self.connection.rollback()
            logger.exception("Data insertion failed.")
            raise

    def replace_table(self, dataframe: pd.DataFrame) -> None:
        """Replace table contents while preserving the controlled schema."""
        self.validate_connection()
        if dataframe.empty:
            raise ValueError("Cannot replace table with an empty dataframe.")
        self.create_table(dataframe)
        try:
            self.cursor.execute(f"DELETE FROM {self._quote_identifier(DATABASE_TABLE)}")
            self.connection.commit()
            self.insert_dataframe(dataframe, if_exists="append")
        except Exception:
            self.connection.rollback()
            logger.exception("Table refresh failed.")
            raise

    def verify_table(self) -> None:
        """Verify table existence, required columns and incident_id primary key."""
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

    def execute_query(self, query: str, parameters: tuple = ()) -> None:
        """Execute a non-SELECT SQL statement with parameters."""
        self.validate_connection()
        try:
            self.cursor.execute(query, parameters)
            self.connection.commit()
        except sqlite3.Error:
            self.connection.rollback()
            logger.exception("SQL query execution failed.")
            raise

    def fetch_dataframe(self, query: str, parameters: tuple = ()) -> pd.DataFrame:
        """Execute a SELECT query and return a dataframe."""
        self.validate_connection()
        return pd.read_sql_query(query, self.connection, params=parameters)

    def get_row_count(self) -> int:
        """Return total row count."""
        self.validate_connection()
        result = self.cursor.execute(
            f"SELECT COUNT(*) FROM {self._quote_identifier(DATABASE_TABLE)}"
        ).fetchone()
        return int(result[0])

    def get_table_schema(self) -> pd.DataFrame:
        """Return SQLite table schema."""
        self.validate_connection()
        return pd.read_sql_query(
            f"PRAGMA table_info({self._quote_identifier(DATABASE_TABLE)})",
            self.connection,
        )

    def export_query_results(self, query: str, output_file=None) -> None:
        """Export query results to CSV."""
        output_path = Path(output_file or (OUTPUT_DIR / "query_results.csv"))
        output_path.parent.mkdir(parents=True, exist_ok=True)
        self.fetch_dataframe(query).to_csv(output_path, index=False)

    def preview_table(self, rows: int = 5) -> pd.DataFrame:
        """Return first N rows from the table."""
        if rows < 1:
            raise ValueError("rows must be at least 1.")
        return self.fetch_dataframe(
            f"SELECT * FROM {self._quote_identifier(DATABASE_TABLE)} LIMIT ?",
            (rows,),
        )

    def close(self) -> None:
        """Close SQLite connection safely."""
        if self.connection is not None:
            self.connection.close()
            self.connection = None
            self.cursor = None

    def run(self) -> pd.DataFrame:
        """Execute complete database integration flow."""
        try:
            self.connect()
            dataframe = self.load_engineered_dataset()
            self.create_table(dataframe)
            self.replace_table(dataframe)
            self.verify_table()
            self.verify_dataframe_schema(dataframe)
            row_count = self.get_row_count()
            if row_count != len(dataframe):
                raise ValueError(
                    f"Database row-count mismatch: expected {len(dataframe)}, got {row_count}."
                )
            return dataframe
        except Exception:
            logger.exception("Database Pipeline failed.")
            raise
        finally:
            self.close()


if __name__ == "__main__":
    manager = DatabaseManager()
    dataframe = manager.run()
    print("\n" + "=" * 70)
    print("DATABASE PIPELINE COMPLETED")
    print("=" * 70)
    print(f"Rows Inserted : {len(dataframe)}")
    print(f"Database File : {DATABASE_FILE}")
    print(f"Table Name    : {DATABASE_TABLE}")
    print("=" * 70)
