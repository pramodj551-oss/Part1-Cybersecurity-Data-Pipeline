"""
Database Module

Stores the feature engineered cybersecurity
incident dataset into SQLite database.

Author:
Pramod Prakash Jadhav
"""

from __future__ import annotations

import logging
import sqlite3

import pandas as pd

from src.config import (
    DATABASE_FILE,
    DATABASE_TABLE,
    ENGINEERED_DATA_FILE,
    LOG_FILE,
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


class DatabaseManager:
    """
    SQLite Database Manager.

    Responsibilities
    ----------------
    - Connect database
    - Create tables
    - Insert dataframe
    - Execute SQL queries
    - Retrieve records
    """

    def __init__(
        self,
        database_path=DATABASE_FILE,
    ):

        self.database_path = database_path

        self.connection = None

        self.cursor = None

        logger.info(
            "DatabaseManager initialized."
        )

    # ======================================================
    # Connect Database
    # ======================================================

    def connect(self):
        """
        Establish SQLite connection.
        """

        logger.info(
            "Connecting to SQLite database..."
        )

        try:

            self.connection = sqlite3.connect(
                self.database_path
            )

            self.cursor = (
                self.connection.cursor()
            )

            logger.info(
                "Database connection established."
            )

        except sqlite3.Error as error:

            logger.exception(
                "Database connection failed."
            )

            raise error

    # ======================================================
    # Validate Connection
    # ======================================================

    def validate_connection(self):
        """
        Ensure database connection exists.
        """

        if self.connection is None:

            raise ConnectionError(
                "Database connection is not established."
            )

    # ======================================================
    # Load Engineered Dataset
    # ======================================================

    @staticmethod
    def load_engineered_dataset():
        """
        Load feature engineered dataset.
        """

        logger.info(
            "Loading engineered dataset..."
        )

        dataframe = pd.read_csv(
            ENGINEERED_DATA_FILE,
            parse_dates=["incident_date"],
        )

        if dataframe.empty:

            raise ValueError(
                "Engineered dataset is empty."
            )

        logger.info(
            "Engineered dataset loaded successfully."
        )

        return dataframe

    # ======================================================
    # Database Information
    # ======================================================

    def database_info(self):
        """
        Display database information.
        """

        self.validate_connection()

        print("\n" + "=" * 60)
        print("DATABASE INFORMATION")
        print("=" * 60)

        print(
            f"Database : {self.database_path}"
        )

        print(
            f"Table    : {DATABASE_TABLE}"
        )

        print("=" * 60)
          # ======================================================
    # Create Table
    # ======================================================

    def create_table(self):
        """
        Create database table if it does not exist.
        """

        self.validate_connection()

        logger.info("Creating database table...")

        try:

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

            self.cursor.execute(create_table_query)

            self.connection.commit()

            logger.info(
                "Database table created successfully."
            )

        except sqlite3.Error as error:

            self.connection.rollback()

            logger.exception(
                "Table creation failed."
            )

            raise error

    # ======================================================
    # Insert DataFrame
    # ======================================================

    def insert_dataframe(
        self,
        dataframe: pd.DataFrame,
        if_exists: str = "replace",
    ):
        """
        Insert dataframe into SQLite database.

        Parameters
        ----------
        dataframe : pandas.DataFrame

        if_exists : str

            replace | append
        """

        self.validate_connection()

        if dataframe.empty:

            raise ValueError(
                "Cannot insert empty dataframe."
            )

        logger.info(
            "Inserting dataframe into database..."
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

            logger.info(

                "%d rows inserted.",

                len(dataframe),

            )

        except Exception as error:

            self.connection.rollback()

            logger.exception(
                "Data insertion failed."
            )

            raise error

    # ======================================================
    # Replace Existing Data
    # ======================================================

    def replace_table(
        self,
        dataframe: pd.DataFrame,
    ):
        """
        Replace existing table
        with latest dataset.
        """

        logger.info(
            "Replacing database table..."
        )

        self.insert_dataframe(

            dataframe,

            if_exists="replace",

        )

    # ======================================================
    # Append New Records
    # ======================================================

    def append_table(
        self,
        dataframe: pd.DataFrame,
    ):
        """
        Append new records
        to existing table.
        """

        logger.info(
            "Appending records..."
        )

        self.insert_dataframe(

            dataframe,

            if_exists="append",

        )

    # ======================================================
    # Verify Table
    # ======================================================

    def verify_table(self):
        """
        Verify table exists.
        """

        self.validate_connection()

        query = """

        SELECT name

        FROM sqlite_master

        WHERE type='table'

        """

        tables = pd.read_sql_query(

            query,

            self.connection,

        )

        if DATABASE_TABLE not in tables["name"].values:

            raise ValueError(
                "Database table not found."
            )

        logger.info(
            "Table verification successful."
)
          # ======================================================
    # Execute SQL Query
    # ======================================================

    def execute_query(self, query: str):
        """
        Execute SQL query.

        Parameters
        ----------
        query : str
            SQL query string.
        """

        self.validate_connection()

        logger.info("Executing SQL query...")

        try:

            self.cursor.execute(query)

            self.connection.commit()

            logger.info(
                "SQL query executed successfully."
            )

        except sqlite3.Error as error:

            self.connection.rollback()

            logger.exception(
                "SQL query execution failed."
            )

            raise error

    # ======================================================
    # Fetch DataFrame
    # ======================================================

    def fetch_dataframe(
        self,
        query: str,
    ) -> pd.DataFrame:
        """
        Execute SELECT query and
        return DataFrame.
        """

        self.validate_connection()

        logger.info(
            "Fetching query results..."
        )

        try:

            dataframe = pd.read_sql_query(

                query,

                self.connection,

            )

            logger.info(

                "%d rows fetched.",

                len(dataframe),

            )

            return dataframe

        except sqlite3.Error as error:

            logger.exception(
                "Data fetch failed."
            )

            raise error

    # ======================================================
    # Get Row Count
    # ======================================================

    def get_row_count(self) -> int:
        """
        Return total number of rows
        in the database table.
        """

        self.validate_connection()

        query = f"""

        SELECT COUNT(*)

        FROM {DATABASE_TABLE}

        """

        self.cursor.execute(query)

        count = self.cursor.fetchone()[0]

        logger.info(
            "Table contains %d rows.",
            count,
        )

        return count

    # ======================================================
    # Get Table Schema
    # ======================================================

    def get_table_schema(self) -> pd.DataFrame:
        """
        Return database schema.
        """

        self.validate_connection()

        query = f"""

        PRAGMA table_info(
            {DATABASE_TABLE}
        )

        """

        schema = pd.read_sql_query(

            query,

            self.connection,

        )

        logger.info(
            "Table schema retrieved."
        )

        return schema

    # ======================================================
    # Export Query Results
    # ======================================================

    def export_query_results(
        self,
        query: str,
        output_file=QUERY_RESULTS_FILE,
    ):
        """
        Export SQL query results
        to CSV file.
        """

        logger.info(
            "Exporting query results..."
        )

        dataframe = self.fetch_dataframe(
            query
        )

        dataframe.to_csv(

            output_file,

            index=False,

        )

        logger.info(
            "Query results exported to %s",
            output_file,
        )

    # ======================================================
    # Preview Table
    # ======================================================

    def preview_table(
        self,
        rows: int = 5,
    ) -> pd.DataFrame:
        """
        Return first N rows
        from database table.
        """

        query = f"""

        SELECT *

        FROM {DATABASE_TABLE}

        LIMIT {rows}

        """

        return self.fetch_dataframe(query)
          # ======================================================
    # Close Database Connection
    # ======================================================

    def close(self):
        """
        Close SQLite database connection.
        """

        if self.connection is not None:

            self.connection.close()

            self.connection = None

            self.cursor = None

            logger.info(
                "Database connection closed."
            )

    # ======================================================
    # Complete Database Pipeline
    # ======================================================

    def run(self):
        """
        Execute complete database pipeline.

        Returns
        -------
        pandas.DataFrame
            Loaded engineered dataframe.
        """

        logger.info("=" * 60)
        logger.info("Starting Database Pipeline")
        logger.info("=" * 60)

        try:

            # Connect

            self.connect()

            # Load Engineered Dataset

            dataframe = self.load_engineered_dataset()

            # Create Table

            self.create_table()

            # Insert Data

            self.replace_table(dataframe)

            # Verify

            self.verify_table()

            # Information

            self.database_info()

            logger.info(
                "Database Pipeline completed successfully."
            )

            return dataframe

        except Exception as error:

            logger.exception(
                "Database Pipeline failed."
            )

            raise error

        finally:

            self.close()
          # ==========================================================
# Standalone Execution
# ==========================================================

if __name__ == "__main__":

    try:

        manager = DatabaseManager()

        dataframe = manager.run()

        print("\n" + "=" * 70)
        print("DATABASE PIPELINE COMPLETED")
        print("=" * 70)

        print(
            f"Rows Inserted : {len(dataframe)}"
        )

        print(
            f"Database File : {DATABASE_FILE}"
        )

        print(
            f"Table Name    : {DATABASE_TABLE}"
        )

        print("=" * 70)

    except Exception as error:

        print("\nDatabase Error")

        print(error)
      
