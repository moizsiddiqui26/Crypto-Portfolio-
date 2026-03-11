import pandas as pd

def load_data():
    return pd.read_csv("preprocessed_data.csv", index_col=0, parse_dates=True)
