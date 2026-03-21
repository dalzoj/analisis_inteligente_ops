import csv
import os
from datetime import datetime

STORAGE_PTH = ".storage"
CSV_PATH    = os.path.join(STORAGE_PTH, "responses.csv")

_FIELDNAMES = ["timestamp","type_response","mode","model_name","tokens_in","tokens_out","answer",]


def _ensure_file():
    os.makedirs(STORAGE_PTH, exist_ok=True)
    if not os.path.exists(CSV_PATH):
        with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=_FIELDNAMES)
            writer.writeheader()


def _flatten(text):
    return " ".join(text.split())

def save_response(response):
    print("INFO: storage -> save_response")
    try:
        _ensure_file()
        row = {
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "type_response": response.type_response,
            "mode": response.mode,
            "model_name": response.model_name,
            "tokens_in": response.tokens_in,
            "tokens_out": response.tokens_out,
            "answer": _flatten(response.answer)
        }
        with open(CSV_PATH, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=_FIELDNAMES)
            writer.writerow(row)

    except Exception as ex:
        print(f"ERROR: storage -> save_response -> {ex}")