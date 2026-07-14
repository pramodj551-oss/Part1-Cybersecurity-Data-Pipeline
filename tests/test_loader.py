import pandas as pd

from src.data_loader import DataLoader


def test_dataset_loads():

    loader = DataLoader()

    df = loader.run()

    assert isinstance(df, pd.DataFrame)

    assert not df.empty
