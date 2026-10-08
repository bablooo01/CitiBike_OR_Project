import pandas as pd
from pathlib import Path


# ==================================================
# PATHS
# ==================================================

RAW_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = PROCESSED_DIR / "june_2026_clean.csv"


# ==================================================
# FIND FILES
# ==================================================

files = sorted(RAW_DIR.glob("*.csv"))

print(f"Found {len(files)} files.")


# ==================================================
# PROCESS EACH FILE
# ==================================================

first_write = True

total_rows = 0


for file in files:

    print("\n" + "=" * 60)
    print("Processing:", file.name)
    print("=" * 60)

    for chunk in pd.read_csv(
        file,
        chunksize=100_000,
        low_memory=False
    ):

        # --------------------------------------------------
        # Convert timestamps
        # --------------------------------------------------

        chunk["started_at"] = pd.to_datetime(
            chunk["started_at"],
            errors="coerce"
        )

        chunk["ended_at"] = pd.to_datetime(
            chunk["ended_at"],
            errors="coerce"
        )


        # --------------------------------------------------
        # Keep June 2026
        # --------------------------------------------------

        chunk = chunk[
            (chunk["started_at"] >= "2026-06-01") &
            (chunk["started_at"] < "2026-07-01")
        ]


        # --------------------------------------------------
        # Remove missing station IDs
        # --------------------------------------------------

        chunk = chunk.dropna(
            subset=[
                "start_station_id",
                "end_station_id"
            ]
        )


        # --------------------------------------------------
        # Ride duration
        # --------------------------------------------------

        chunk["ride_duration_min"] = (
            chunk["ended_at"] -
            chunk["started_at"]
        ).dt.total_seconds() / 60


        # --------------------------------------------------
        # Remove invalid durations
        # --------------------------------------------------

        chunk = chunk[
            (chunk["ride_duration_min"] > 0) &
            (chunk["ride_duration_min"] <= 1440)
        ]


        # --------------------------------------------------
        # Time features
        # --------------------------------------------------

        chunk["date"] = (
            chunk["started_at"].dt.date
        )

        chunk["hour"] = (
            chunk["started_at"].dt.hour
        )

        chunk["day_of_week"] = (
            chunk["started_at"].dt.day_name()
        )


        # --------------------------------------------------
        # Append to output CSV
        # --------------------------------------------------

        chunk.to_csv(
            OUTPUT_FILE,
            mode="w" if first_write else "a",
            header=first_write,
            index=False
        )

        first_write = False

        total_rows += len(chunk)

        print(
            f"Processed rows: {total_rows:,}",
            end="\r"
        )


# ==================================================
# FINISHED
# ==================================================

print("\n\n" + "=" * 60)
print("PREPROCESSING COMPLETE")
print("=" * 60)

print(f"Clean rows: {total_rows:,}")

print("Output:")
print(OUTPUT_FILE)