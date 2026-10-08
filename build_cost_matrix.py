import pandas as pd
import numpy as np
from pathlib import Path


# ============================================================
# PATHS
# ============================================================

DATA_DIR = Path("data/processed")

SUPPLY_FILE = DATA_DIR / "optimization_supply.csv"
DEMAND_FILE = DATA_DIR / "optimization_demand.csv"

OUTPUT_FILE = DATA_DIR / "transportation_cost_matrix.csv"


# ============================================================
# LOAD DATA
# ============================================================

print("Loading optimization data...")

supply = pd.read_csv(SUPPLY_FILE)
demand = pd.read_csv(DEMAND_FILE)

print("Supply stations:", len(supply))
print("Demand stations:", len(demand))


# ============================================================
# HAVERSINE DISTANCE
# ============================================================

def haversine(lat1, lon1, lat2, lon2):

    R = 6371.0  # Earth radius in km

    lat1 = np.radians(lat1)
    lon1 = np.radians(lon1)

    lat2 = np.radians(lat2)
    lon2 = np.radians(lon2)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        np.sin(dlat / 2) ** 2
        +
        np.cos(lat1)
        * np.cos(lat2)
        * np.sin(dlon / 2) ** 2
    )

    c = 2 * np.arcsin(
        np.sqrt(a)
    )

    return R * c


# ============================================================
# CREATE ALL SUPPLY-DEMAND PAIRS
# ============================================================

rows = []

for _, s in supply.iterrows():

    for _, d in demand.iterrows():

        distance = haversine(
            s["latitude"],
            s["longitude"],
            d["latitude"],
            d["longitude"]
        )

        rows.append({
            "supply_station_id": s["station_id"],
            "supply_station_name": s["station_name"],
            "demand_station_id": d["station_id"],
            "demand_station_name": d["station_name"],
            "distance_km": distance
        })


# ============================================================
# CREATE DATAFRAME
# ============================================================

cost_matrix = pd.DataFrame(rows)


# ============================================================
# SAVE
# ============================================================

cost_matrix.to_csv(
    OUTPUT_FILE,
    index=False
)


# ============================================================
# RESULTS
# ============================================================

print("\n" + "=" * 60)
print("TRANSPORTATION COST MATRIX")
print("=" * 60)

print(
    "Number of routes:",
    len(cost_matrix)
)

print(
    "Minimum distance:",
    round(
        cost_matrix["distance_km"].min(),
        3
    ),
    "km"
)

print(
    "Maximum distance:",
    round(
        cost_matrix["distance_km"].max(),
        3
    ),
    "km"
)

print(
    "Average distance:",
    round(
        cost_matrix["distance_km"].mean(),
        3
    ),
    "km"
)


print("\nClosest 10 station pairs:")

print(
    cost_matrix
    .sort_values("distance_km")
    .head(10)
    .to_string(index=False)
)


print("\nSaved:")
print(OUTPUT_FILE)