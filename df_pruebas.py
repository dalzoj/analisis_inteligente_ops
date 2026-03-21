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

df_metrics = get_df_metrics()
df_orders = get_df_orders()

print(df_metrics.columns)
print(df_orders.columns)

print(df_metrics[df_metrics['METRIC'] == 'Lead Penetration'])

result = df_metrics[df_metrics['METRIC'] == 'Lead Penetration'].nlargest(5, 'L0W_ROLL')[['ZONE', 'L0W_ROLL']].reset_index(drop=True)

print(result)