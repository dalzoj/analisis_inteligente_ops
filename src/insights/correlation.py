import configparser
import pandas as pd

config = configparser.ConfigParser()
config.read("config/config.cfg")


def _one_month_mean(df):
    week_cols = [c for c in df.columns if c.startswith("L") and c.endswith("W_ROLL")]
    week_cols_sorted = sorted(week_cols)
    recent = week_cols_sorted[:4]
    return df[recent].mean(axis=1)


def detect(df: pd.DataFrame) -> list[dict]:
    threshold = config.getfloat("insights", "correlation_threshold")

    df = df.copy()
    df["_value"] = _one_month_mean(df)

    pivot = df.pivot_table(
        index=["COUNTRY", "CITY", "ZONE"],
        columns="METRIC",
        values="_value",
    )

    pivot = pivot.dropna(axis=1, thresh=int(len(pivot) * 0.5))

    if pivot.shape[1] < 2:
        return []
    

    corr_matrix = pivot.corr()
    n_zones = len(pivot)

    findings = []
    checked = set()

    for metric_a in corr_matrix.columns:
        for metric_b in corr_matrix.columns:
            if metric_a >= metric_b:
                continue
            if (metric_a, metric_b) in checked:
                continue
            checked.add((metric_a, metric_b))
            

            r = corr_matrix.loc[metric_a, metric_b]
            if abs(r) < threshold:
                continue

            both = pivot[[metric_a, metric_b]].dropna()
            if r > 0:
                top_zones = both.sum(axis=1).nlargest(3).index.tolist()
            else:
                top_zones = (both[metric_a] - both[metric_b]).nlargest(3).index.tolist()

            findings.append({
                "metric_a": metric_a,
                "metric_b": metric_b,
                "correlation": round(r, 3),
                "direction": "positiva" if r > 0 else "negativa",
                "n_zones": n_zones,
                "example_zones": [list(z) for z in top_zones],
            })

    findings.sort(key=lambda x: abs(x["correlation"]), reverse=True)
    return findings