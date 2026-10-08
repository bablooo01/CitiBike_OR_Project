import pandas as pd
from pathlib import Path


# ============================================================
# PATHS
# ============================================================

INPUT_FILE = Path(
    "data/processed/june_2026_clean_fixed.csv"
)

OUTPUT_DIR = Path(
    "data/processed"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# LOAD DATA
# ============================================================

print("Loading corrected dataset...")

data = pd.read_csv(
    INPUT_FILE,
    low_memory=False
)

print(
    "Total rows:",
    f"{len(data):,}"
)


# ============================================================
# CONVERT TIMESTAMP
# ============================================================

data["started_at"] = pd.to_datetime(
    data["started_at"],
    errors="coerce"
)


# ============================================================
# SELECT EVENING PEAK
# 17:00 - 18:59
# ============================================================

data["hour"] = data["started_at"].dt.hour

peak_data = data[
    data["hour"].isin([17, 18])
].copy()


print("\nEvening peak trips:")

print(
    f"{len(peak_data):,}"
)


# ============================================================
# DEPARTURES BY STATION
# ============================================================

departures = (
    peak_data
    .groupby("start_station_id")
    .size()
    .reset_index(
        name="departures"
    )
)


# ============================================================
# ARRIVALS BY STATION
# ============================================================

arrivals = (
    peak_data
    .groupby("end_station_id")
    .size()
    .reset_index(
        name="arrivals"
    )
)


# ============================================================
# STATION INFORMATION
# ============================================================

station_info_start = (
    peak_data[
        [
            "start_station_id",
            "start_station_name",
            "start_lat",
            "start_lng"
        ]
    ]
    .drop_duplicates(
        "start_station_id"
    )
)

station_info_start = station_info_start.rename(
    columns={
        "start_station_id": "station_id",
        "start_station_name": "station_name",
        "start_lat": "latitude",
        "start_lng": "longitude"
    }
)


station_info_end = (
    peak_data[
        [
            "end_station_id",
            "end_station_name",
            "end_lat",
            "end_lng"
        ]
    ]
    .drop_duplicates(
        "end_station_id"
    )
)

station_info_end = station_info_end.rename(
    columns={
        "end_station_id": "station_id",
        "end_station_name": "station_name",
        "end_lat": "latitude",
        "end_lng": "longitude"
    }
)


# ============================================================
# COMBINE STATION INFORMATION
# ============================================================

station_info = pd.concat(
    [
        station_info_start,
        station_info_end
    ],
    ignore_index=True
)

station_info = (
    station_info
    .drop_duplicates(
        "station_id"
    )
)


# ============================================================
# COMBINE DEMAND
# ============================================================

station = pd.merge(
    station_info,
    departures,
    left_on="station_id",
    right_on="start_station_id",
    how="outer"
)

station = pd.merge(
    station,
    arrivals,
    left_on="station_id",
    right_on="end_station_id",
    how="outer"
)


# ============================================================
# CLEAN COLUMNS
# ============================================================

station["departures"] = (
    station["departures"]
    .fillna(0)
)

station["arrivals"] = (
    station["arrivals"]
    .fillna(0)
)


# ============================================================
# NET FLOW
# ============================================================

station["net_flow"] = (
    station["arrivals"]
    -
    station["departures"]
)


# ============================================================
# TOTAL ACTIVITY
# ============================================================

station["total_activity"] = (
    station["arrivals"]
    +
    station["departures"]
)


# ============================================================
# DEFINE SURPLUS / DEFICIT
# ============================================================

station["status"] = "Balanced"


station.loc[
    station["net_flow"] > 0,
    "status"
] = "Surplus"


station.loc[
    station["net_flow"] < 0,
    "status"
] = "Deficit"


# ============================================================
# FINAL COLUMNS
# ============================================================

station = station[
    [
        "station_id",
        "station_name",
        "latitude",
        "longitude",
        "departures",
        "arrivals",
        "net_flow",
        "total_activity",
        "status"
    ]
]


# ============================================================
# REMOVE STATIONS WITH VERY LOW ACTIVITY
# ============================================================

# Keep stations with at least 10 peak-period trips.
station = station[
    station["total_activity"] >= 10
].copy()


# ============================================================
# SAVE COMPLETE PEAK DATASET
# ============================================================

output_file = (
    OUTPUT_DIR /
    "evening_peak_station_demand.csv"
)

station.to_csv(
    output_file,
    index=False
)


# ============================================================
# DISPLAY RESULTS
# ============================================================

print("\n" + "=" * 60)
print("EVENING PEAK STATION DATASET")
print("=" * 60)

print(
    "Stations:",
    len(station)
)

print(
    "Surplus:",
    (station["status"] == "Surplus").sum()
)

print(
    "Deficit:",
    (station["status"] == "Deficit").sum()
)

print(
    "Balanced:",
    (station["status"] == "Balanced").sum()
)


# ============================================================
# TOP SURPLUS
# ============================================================

print("\nTOP 10 SURPLUS STATIONS")

print(
    station
    .sort_values(
        "net_flow",
        ascending=False
    )
    .head(10)
    .to_string(index=False)
)


# ============================================================
# TOP DEFICIT
# ============================================================

print("\nTOP 10 DEFICIT STATIONS")

print(
    station
    .sort_values(
        "net_flow",
        ascending=True
    )
    .head(10)
    .to_string(index=False)
)


print("\nSaved:")
print(output_file)