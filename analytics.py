import pandas as pd
from pathlib import Path


# ============================================================
# PATHS
# ============================================================

INPUT_FILE = Path("data/processed/june_2026_clean.csv")

OUTPUT_DIR = Path("data/processed")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# LOAD CLEAN DATA
# ============================================================

print("Loading cleaned dataset...")

data = pd.read_csv(
    INPUT_FILE,
    low_memory=False
)

print("Dataset loaded successfully.")
print("Shape:", data.shape)


# ============================================================
# BASIC DATASET STATISTICS
# ============================================================

print("\n" + "=" * 60)
print("BASIC DATASET STATISTICS")
print("=" * 60)

print("Total rides:", f"{len(data):,}")

print(
    "Average ride duration:",
    round(data["ride_duration_min"].mean(), 2),
    "minutes"
)

print(
    "Median ride duration:",
    round(data["ride_duration_min"].median(), 2),
    "minutes"
)

print(
    "Minimum ride duration:",
    round(data["ride_duration_min"].min(), 2),
    "minutes"
)

print(
    "Maximum ride duration:",
    round(data["ride_duration_min"].max(), 2),
    "minutes"
)


# ============================================================
# MEMBER VS CASUAL
# ============================================================

print("\n" + "=" * 60)
print("MEMBER VS CASUAL")
print("=" * 60)

user_type = data["member_casual"].value_counts()

print(user_type)

print("\nPercentage:")

print(
    (data["member_casual"].value_counts(normalize=True) * 100)
    .round(2)
)


# ============================================================
# RIDEABLE TYPE
# ============================================================

print("\n" + "=" * 60)
print("RIDEABLE TYPE")
print("=" * 60)

print(data["rideable_type"].value_counts())


# ============================================================
# HOURLY DEMAND
# ============================================================

hourly_demand = (
    data.groupby("hour")
    .size()
    .reset_index(name="ride_count")
)

print("\n" + "=" * 60)
print("HOURLY DEMAND")
print("=" * 60)

print(hourly_demand)


# Save
hourly_demand.to_csv(
    OUTPUT_DIR / "hourly_demand.csv",
    index=False
)


# ============================================================
# DAILY DEMAND
# ============================================================

daily_demand = (
    data.groupby("date")
    .size()
    .reset_index(name="ride_count")
)

print("\n" + "=" * 60)
print("DAILY DEMAND")
print("=" * 60)

print(daily_demand)


daily_demand.to_csv(
    OUTPUT_DIR / "daily_demand.csv",
    index=False
)


# ============================================================
# DAY OF WEEK DEMAND
# ============================================================

weekday_demand = (
    data.groupby("day_of_week")
    .size()
    .reset_index(name="ride_count")
)

print("\n" + "=" * 60)
print("DAY OF WEEK DEMAND")
print("=" * 60)

print(weekday_demand)


weekday_demand.to_csv(
    OUTPUT_DIR / "weekday_demand.csv",
    index=False
)


# ============================================================
# START STATION STATISTICS
# ============================================================

departures = (
    data.groupby(
        [
            "start_station_id",
            "start_station_name",
            "start_lat",
            "start_lng"
        ]
    )
    .size()
    .reset_index(name="departures")
)


departures = departures.rename(
    columns={
        "start_station_id": "station_id",
        "start_station_name": "station_name",
        "start_lat": "latitude",
        "start_lng": "longitude"
    }
)


# ============================================================
# END STATION STATISTICS
# ============================================================

arrivals = (
    data.groupby(
        [
            "end_station_id",
            "end_station_name",
            "end_lat",
            "end_lng"
        ]
    )
    .size()
    .reset_index(name="arrivals")
)


arrivals = arrivals.rename(
    columns={
        "end_station_id": "station_id",
        "end_station_name": "station_name",
        "end_lat": "latitude",
        "end_lng": "longitude"
    }
)


# ============================================================
# MERGE ARRIVALS + DEPARTURES
# ============================================================

station_stats = pd.merge(
    departures,
    arrivals,
    on="station_id",
    how="outer",
    suffixes=("_start", "_end")
)


# ============================================================
# FILL MISSING VALUES
# ============================================================

station_stats["departures"] = (
    station_stats["departures"]
    .fillna(0)
)

station_stats["arrivals"] = (
    station_stats["arrivals"]
    .fillna(0)
)


# ============================================================
# STATION NAME
# ============================================================

station_stats["station_name"] = (
    station_stats["station_name_start"]
    .fillna(
        station_stats["station_name_end"]
    )
)


# ============================================================
# COORDINATES
# ============================================================

station_stats["latitude"] = (
    station_stats["latitude_start"]
    .fillna(
        station_stats["latitude_end"]
    )
)

station_stats["longitude"] = (
    station_stats["longitude_start"]
    .fillna(
        station_stats["longitude_end"]
    )
)


# ============================================================
# NET FLOW
# ============================================================

station_stats["net_flow"] = (
    station_stats["arrivals"]
    -
    station_stats["departures"]
)


# ============================================================
# TOTAL ACTIVITY
# ============================================================

station_stats["total_activity"] = (
    station_stats["arrivals"]
    +
    station_stats["departures"]
)


# ============================================================
# STATION STATUS
# ============================================================

station_stats["status"] = "Balanced"

station_stats.loc[
    station_stats["net_flow"] > 0,
    "status"
] = "Surplus"

station_stats.loc[
    station_stats["net_flow"] < 0,
    "status"
] = "Deficit"


# ============================================================
# CLEAN FINAL TABLE
# ============================================================

station_stats = station_stats[
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
# SORT BY ACTIVITY
# ============================================================

station_stats = station_stats.sort_values(
    "total_activity",
    ascending=False
)


# ============================================================
# SAVE
# ============================================================

station_file = (
    OUTPUT_DIR /
    "station_statistics.csv"
)

station_stats.to_csv(
    station_file,
    index=False
)


# ============================================================
# DISPLAY IMPORTANT RESULTS
# ============================================================

print("\n" + "=" * 60)
print("STATION STATISTICS")
print("=" * 60)

print(
    "Number of stations:",
    len(station_stats)
)

print("\nTop 10 busiest stations:")

print(
    station_stats.head(10).to_string(
        index=False
    )
)


print("\n" + "=" * 60)
print("STATION STATUS")
print("=" * 60)

print(
    station_stats["status"]
    .value_counts()
)


print("\n" + "=" * 60)
print("TOP SURPLUS STATIONS")
print("=" * 60)

print(
    station_stats
    .sort_values(
        "net_flow",
        ascending=False
    )
    .head(10)
    .to_string(index=False)
)


print("\n" + "=" * 60)
print("TOP DEFICIT STATIONS")
print("=" * 60)

print(
    station_stats
    .sort_values(
        "net_flow",
        ascending=True
    )
    .head(10)
    .to_string(index=False)
)


print("\n" + "=" * 60)
print("ANALYTICS COMPLETE")
print("=" * 60)

print("Saved files:")
print(" - hourly_demand.csv")
print(" - daily_demand.csv")
print(" - weekday_demand.csv")
print(" - station_statistics.csv")