import pandas as pd
import pytest

from src.config import EXPECTED_COLUMNS
from src.data_loader import DataLoader


def test_dataset_loads():
    loader = DataLoader()
    df = loader.run()

    assert isinstance(df, pd.DataFrame)
    assert not df.empty


def test_dataset_contains_required_columns():
    loader = DataLoader()
    df = loader.run()

    missing_columns = [column for column in EXPECTED_COLUMNS if column not in df.columns]

    assert not missing_columns, f"Dataset is missing required columns: {missing_columns}"


def test_missing_dataset_raises_file_not_found(tmp_path):
    loader = DataLoader(file_path=tmp_path / "missing.csv")

    with pytest.raises(FileNotFoundError, match="Dataset not found"):
        loader.load_csv()
