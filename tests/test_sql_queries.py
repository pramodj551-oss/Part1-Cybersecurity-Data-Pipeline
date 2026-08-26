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
    """Extract the 29 numbered SQL statements without being confused by comments."""
    text = QUERIES_FILE.read_text(encoding="utf-8")
    matches = re.findall(
        r"(?ms)^\s*--\s*(\d+)\.\s+.*?\n(.*?)(?=^\s*--\s*\d+\.\s+|\Z)",
        text,
    )
    queries = []
    for number, body in matches:
        statement = re.sub(r"(?m)^\s*--.*(?:\n|$)", "", body).strip()
        statement = statement.rstrip(";").strip()
        if statement:
            queries.append((int(number), statement))
    queries.sort(key=lambda item: item[0])
    return [statement for _, statement in queries]


def test_queries_file_contains_29_queries() -> None:
    queries = _load_queries()
    assert len(queries) == 29, f"Expected 29 SQL queries, found {len(queries)}"


def test_all_29_queries_execute_against_engineered_dataset() -> None:
    if not ENGINEERED_DATA_FILE.exists():
        pytest.skip("Engineered dataset is created by the end-to-end pipeline step")

    dataframe = pd.read_csv(ENGINEERED_DATA_FILE)
    assert not dataframe.empty, "Engineered dataset is empty"

    connection = sqlite3.connect(":memory:")
    try:
        dataframe.to_sql(DATABASE_TABLE, connection, index=False, if_exists="replace")
        queries = _load_queries()
        assert len(queries) == 29

        failures: list[str] = []
        for index, query in enumerate(queries, start=1):
            try:
                pd.read_sql_query(query, connection)
            except Exception as exc:
                failures.append(f"Query {index}: {exc}")

        assert not failures, "SQL integration failures:\n" + "\n".join(failures)
    finally:
        connection.close()
