import configparser
import pandas as pd

config = configparser.ConfigParser()
config.read("config/config.cfg")


def _is_consistently_declining(values):
    return all(values[i] < values[i - 1] for i in range(1, len(values)))


def _is_consistently_improving(values):
    return all(values[i] > values[i - 1] for i in range(1, len(values)))


def detect(df):

    week_cols = [c for c in df.columns if c.startswith("L") and c.endswith("W_ROLL")]

    min_weeks = config.getint("insights", "trend_min_weeks")

    available = [col for col in week_cols if col in df.columns]

    recent_weeks = available[-(min_weeks + 1):]

    if len(recent_weeks) < 2:
        return []

    findings = []

    for _, row in df.iterrows():
        values = [row[col] for col in recent_weeks if not pd.isna(row[col])]

        if len(values) < min_weeks + 1:
            continue

        if _is_consistently_declining(values):
            trend = "decrementando"
        
        elif _is_consistently_improving(values):
            trend = "incrementando"
        
        else:
            continue

        findings.append({
            "zone": row["ZONE"],
            "city": row["CITY"],
            "country": row["COUNTRY"],
            "metric": row["METRIC"],
            "trend": trend,
            "weeks_count": min_weeks,
            "week_from": recent_weeks[0],
            "week_to": recent_weeks[-1],
            "start_value": round(values[0], 4),
            "end_value": round(values[-1], 4),
        })

    return findings