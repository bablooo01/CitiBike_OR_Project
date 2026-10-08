import pandas as pd
from pathlib import Path


# ============================================================
# PATHS
# ============================================================

INPUT_FILE = Path(
    "data/processed/june_2026_clean.csv"
)

OUTPUT_FILE = Path(
    "data/processed/june_2026_clean_fixed.csv"
)


# ============================================================
# LOAD DATA
# ============================================================

print("Loading cleaned dataset...")

data = pd.read_csv(
    INPUT_FILE,
    low_memory=False
)

print("Rows:", f"{len(data):,}")


# ============================================================
# NORMALIZE STATION IDs
# ============================================================

def normalize_station_id(value):

    if pd.isna(value):
        return None

    value = str(value).strip()

    try:
        number = float(value)

        # Convert 5980.10 → 5980.1
        return f"{number:.10g}"

    except ValueError:
        return value


print("\nNormalizing station IDs...")

data["start_station_id"] = (
    data["start_station_id"]
    .apply(normalize_station_id)
)

data["end_station_id"] = (
    data["end_station_id"]
    .apply(normalize_station_id)
)


# ============================================================
# CHECK EXAMPLE
# ============================================================

print("\nExample normalized IDs:")

print(
    data[
        [
            "start_station_id",
            "end_station_id"
        ]
    ]
    .head(20)
)


# ============================================================
# SAVE
# ============================================================

print("\nSaving corrected dataset...")

data.to_csv(
    OUTPUT_FILE,
    index=False
)

print("\nDONE!")
print("Output:")
print(OUTPUT_FILE)