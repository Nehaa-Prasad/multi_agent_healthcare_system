import json
import pandas as pd
from pathlib import Path

DATA_PATH = Path("data/fall_events.json")

def load_events():
    # If file missing, return empty list
    if not DATA_PATH.exists():
        return []

    # Try reading whole file as JSON array/object
    try:
        with open(DATA_PATH, "r") as f:
            raw = f.read().strip()
            if not raw:
                return []
            data = json.loads(raw)
    except json.JSONDecodeError:
        # Fallback: try ndjson (one JSON object per line)
        objs = []
        try:
            with open(DATA_PATH, "r") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        objs.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
            return objs
        except Exception:
            return []
    except Exception:
        return []

    # Normalize to list-of-dicts for pandas
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        # If dict is dict-of-lists, let pandas handle it by returning as-is;
        # otherwise wrap single-record dict into a list
        all_values_are_iterable = all(
            isinstance(v, (list, tuple)) for v in data.values()
        )
        if all_values_are_iterable:
            # convert dict-of-lists into a list of records
            return pd.DataFrame.from_dict(data).to_dict(orient="records")
        else:
            return [data]

    # unexpected type
    return []

# Usage:
data = load_events()
# create DataFrame safely
if len(data) == 0:
    df = pd.DataFrame()  # empty DataFrame
else:
    df = pd.DataFrame(data)
