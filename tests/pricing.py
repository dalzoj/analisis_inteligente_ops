import os
import csv
from datetime import date
import configparser

config = configparser.ConfigParser()
config.read("config/config.cfg")

COST_PER_1M_TOKENS_IN  = 0.80
COST_PER_1M_TOKENS_OUT = 4.00


def load_today_responses(path):

    today = date.today().isoformat()
    rows  = []

    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            timestamp = row.get("timestamp", "")
            
            if timestamp.startswith(today):
                rows.append(row)

    return rows


def calculate(rows):
    
    total_in  = 0
    total_out = 0

    for row in rows:
        try:
            total_in  += int(row.get("tokens_in",  0) or 0)
            total_out += int(row.get("tokens_out", 0) or 0)
        except ValueError:
            continue

    cost_in    = (total_in  / 1000000) * COST_PER_1M_TOKENS_IN
    cost_out   = (total_out / 1000000) * COST_PER_1M_TOKENS_OUT
    
    total_cost = cost_in + cost_out

    return total_in, total_out, cost_in, cost_out, total_cost


def main():
    
    path = '.storage/responses.csv'

    today = date.today().isoformat()
    rows  = load_today_responses(path)

    total_in, total_out, cost_in, cost_out, total_cost = calculate(rows)

    print(f"CONSUMIDO HOY ({today})")
    print(f"- Conversaciones: {len(rows)}")
    print(f"- Tokens de entrada: {total_in:>12,}")
    print(f"- Tokens de salida: {total_out:>12,}")
    
    print(f"COSTOS PRELIMINAR ({today})")   
    print(f"- Costo entrada (USD) : $ {cost_in:>10.4f}")
    print(f"- Costo salida (USD) : $ {cost_out:>10.4f}")

    print(f"COSTOS TOTALES ({today})")
    print(f"- COSTO TOTAL (USD) : $ {total_cost:>10.4f}")


if __name__ == "__main__":
    main()