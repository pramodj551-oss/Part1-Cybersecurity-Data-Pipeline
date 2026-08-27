"""
Utility Functions

Shared helper functions for the cybersecurity analytics pipeline.
"""

from pathlib import Path

import pandas as pd


def ensure_directory(path: Path) -> None:
    """Create directory if it does not exist."""
    path.mkdir(parents=True, exist_ok=True)


def dataframe_shape(df: pd.DataFrame) -> str:
    """Return DataFrame shape as a human-readable string."""
    return f"{df.shape[0]} rows × {df.shape[1]} columns"


def report_missing_values(df: pd.DataFrame) -> pd.Series:
    """Return missing-value counts for each DataFrame column, descending."""
    if not isinstance(df, pd.DataFrame):
        raise TypeError("df must be a pandas DataFrame.")

    return df.isna().sum().sort_values(ascending=False)
