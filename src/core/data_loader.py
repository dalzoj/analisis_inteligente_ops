import os
import pandas as pd
import configparser

config = configparser.ConfigParser()
config.read("config/config.cfg")

_num_cols    = [f"L{i}W" for i in range(8, -1, -1)]
_str_cols     = ["COUNTRY", "CITY", "ZONE", "METRIC"]


def get_df_metrics():
    path = os.path.join(config['paths']['metrics_data'])
    return pd.read_csv(
        path, sep=";", decimal=",",
        dtype={
        **{c: "string" for c in _str_cols},
        "ZONE_TYPE": "category",
        "ZONE_PRIORITIZATION": "category",
        **{f"{c}_ROLL": "float32" for c in _num_cols},
    })


def get_df_orders():
    path = os.path.join(config['paths']['orders_data'])
    return pd.read_csv(
        path, sep=";", decimal=",",
        dtype={
        **{c: "string" for c in _str_cols},
        **{c: "float32" for c in _num_cols},
    })