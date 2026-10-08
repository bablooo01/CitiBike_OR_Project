import pandas as pd
from pathlib import Path


FILE = Path(
    "data/processed/june_2026_clean_fixed.csv"
)

data = pd.read_csv(
    FILE,
    low_memory=False
)


# Find all records for this station
station = data[
    data["start_station_id"] == "5980.1"
]

station2 = data[
    data["end_station_id"] == "5980.1"
]


print("E 17 St & Broadway")
print("=" * 50)

print(
    "Departures:",
    len(station)
)

print(
    "Arrivals:",
    len(station2)
)


# Check whether 5980.10 still exists
print("\nChecking old representation...")

print(
    "5980.10 as start:",
    (data["start_station_id"] == "5980.10").sum()
)

print(
    "5980.10 as end:",
    (data["end_station_id"] == "5980.10").sum()
)