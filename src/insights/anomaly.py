import configparser
import pandas as pd

config = configparser.ConfigParser()
config.read("config/config.cfg")


def detect(df):
    print('INFO: anomaly -> detect')

    n_weeks = config.getint("insights", "anomaly_weeks")
    threshold = config.getfloat("insights", "anomaly_threshold")
    
    week_cols = [c for c in df.columns if c.startswith("L") and c.endswith("W_ROLL")]

    available = [col for col in week_cols if col in df.columns]
    
    window = available[-n_weeks:]

    if len(window) < 2:
        return []

    findings = []

    for _, row in df.iterrows():
        for i in range(len(window) - 1):
            old_col = window[i]
            new_col = window[i + 1]

            old_value = row[old_col]
            new_value = row[new_col]

            if old_value == 0 or pd.isna(old_value) or pd.isna(new_value):
                continue

            change = (new_value - old_value) / abs(old_value)

            if abs(change) >= threshold:
                findings.append({
                    "zone": row["ZONE"],
                    "city": row["CITY"],
                    "country": row["COUNTRY"],
                    "metric": row["METRIC"],
                    "week_from": old_col,
                    "week_to": new_col,
                    "previous_value": round(old_value, 4),
                    "current_value": round(new_value, 4),
                    "change_pct": round(change * 100, 2),
                    "direction": "mejora" if change > 0 else "deterioro",
                })

    return findings