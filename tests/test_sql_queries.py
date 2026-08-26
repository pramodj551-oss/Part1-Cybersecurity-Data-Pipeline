"""Integration tests for all SQL queries defined in queries.sql."""

from __future__ import annotations

import re
import sqlite3
from pathlib import Path

import pandas as pd
import pytest

from src.config import DATABASE_TABLE, ENGINEERED_DATA_FILE

ROOT = Path(__file__).resolve().parents[1]
QUERIES_FILE = ROOT / "queries.sql"


def _load_queries() -> list[str]:
    """Split queries.sql into executable SQL statements."""
    text = QUERIES_FILE.read_text(encoding="utf-8")
    statements = [statement.strip() for statement in text.split(";")]
    return [statement for statement in statements if statement and not statement.startswith("--")]


def _strip_comments(statement: str) -> str:
    lines = [line for line in statement.splitlines() if not line.strip().startswith("--")]
    return "\n".join(lines).strip()


def test_queries_file_contains_29_queries() -> None:
    queries = _load_queries()
    assert len(queries) == 29, f"Expected 29 SQL queries, found {len(queries)}"


def test_all_29_queries_execute_against_engineered_dataset() -> None:
    assert ENGINEERED_DATA_FILE.exists(), (
        f"Engineered dataset not found: {ENGINEERED_DATA_FILE}"
    )

    dataframe = pd.read_csv(ENGINEERED_DATA_FILE)
    assert not dataframe.empty, "Engineered dataset is empty"

    connection = sqlite3.connect(":memory:")
    try:
        dataframe.to_sql(DATABASE_TABLE, connection, index=False, if_exists="replace")
        queries = _load_queries()

        failures: list[str] = []
        for index, raw_query in enumerate(queries, start=1):
            query = _strip_comments(raw_query)
            if not query:
                failures.append(f"Query {index}: empty SQL statement")
                continue
            try:
                pd.read_sql_query(query, connection)
            except Exception as exc:
                failures.append(f"Query {index}: {exc}")

        assert not failures, "SQL integration failures:\n" + "\n".join(failures)
    finally:
        connection.close()
