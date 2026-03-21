import configparser
import pandas as pd

config = configparser.ConfigParser()
config.read("config/config.cfg")

GROUP_COLUMNS = ["ZONE_TYPE", "ZONE_PRIORITIZATION", "CITY"]


def detect(df, group_columns):
    try:
        print('INFO: benchmark -> detect')

        min_zones = config.getint("insights", "benchmark_min_zones_per_group")
        threshold = config.getfloat("insights", "benchmark_deviation_threshold")
        num_weeks = config.getint("insights", "benchmark_weeks")

        week_columns = [f"L{i}W_ROLL" for i in range(num_weeks)]

        base_columns = group_columns if group_columns else GROUP_COLUMNS
        group_dims = base_columns + ["METRIC"]
        grouped = df.groupby(group_dims)

        findings = []
        flag_above = False

        for group_keys, group in grouped:
            if len(group) < min_zones:
                continue

            for week_col in week_columns:
                median = group[week_col].median()
                if median == 0:
                    continue

                for _, row in group.iterrows():
                    zone_value = row[week_col]
                    if pd.isna(zone_value):
                        continue

                    deviation = (zone_value - median) / abs(median)

                    is_underperforming = deviation <= -abs(threshold)
                    is_outstanding = flag_above and deviation >= abs(threshold)

                    if not (is_underperforming or is_outstanding):
                        continue

                    findings.append({
                        "zone": row["ZONE"],
                        "city": row["CITY"],
                        "country": row["COUNTRY"],
                        "group_by": base_columns,
                        "group_label": dict(zip(group_dims, group_keys)),
                        "metric": row["METRIC"],
                        "week": week_col,
                        "zone_value": round(zone_value, 4),
                        "group_median": round(median, 4),
                        "deviation_pct": round(deviation * 100, 2),
                        "flag": "underperforming" if is_underperforming else "outstanding",
                    })

        return findings

    except Exception as ex:
        print(f'ERROR: {ex}')
        return False