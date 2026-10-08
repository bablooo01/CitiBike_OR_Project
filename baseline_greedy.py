import pandas as pd
from pathlib import Path


# ============================================================
# PATHS
# ============================================================

DATA_DIR = Path("data/processed")

SUPPLY_FILE = DATA_DIR / "optimization_supply.csv"
DEMAND_FILE = DATA_DIR / "optimization_demand.csv"
COST_FILE = DATA_DIR / "transportation_cost_matrix.csv"

OUTPUT_FILE = DATA_DIR / "greedy_baseline_solution.csv"


# ============================================================
# LOAD DATA
# ============================================================

print("Loading optimization data...")

supply = pd.read_csv(SUPPLY_FILE)
demand = pd.read_csv(DEMAND_FILE)
cost = pd.read_csv(COST_FILE)


# ============================================================
# CREATE REMAINING SUPPLY/DEMAND
# ============================================================

remaining_supply = dict(
    zip(
        supply["station_id"],
        supply["supply"].astype(float)
    )
)

remaining_demand = dict(
    zip(
        demand["station_id"],
        demand["demand"].astype(float)
    )
)


# ============================================================
# GREEDY NEAREST-STATION STRATEGY
# ============================================================

solution = []


# Process largest demand first
demand_order = (
    demand
    .sort_values(
        "demand",
        ascending=False
    )["station_id"]
    .tolist()
)


for destination in demand_order:

    required = remaining_demand[destination]

    if required <= 0:
        continue


    # Find available supply stations
    available = [
        station
        for station in remaining_supply
        if remaining_supply[station] > 0
    ]


    while required > 0 and available:

        # Find nearest available supply station
        candidates = cost[
            (cost["demand_station_id"] == destination)
            &
            (cost["supply_station_id"].isin(available))
        ].copy()


        if candidates.empty:
            break


        nearest = candidates.loc[
            candidates["distance_km"].idxmin()
        ]


        source = nearest["supply_station_id"]

        distance = nearest["distance_km"]


        # Amount to move
        amount = min(
            required,
            remaining_supply[source]
        )


        # Record route
        solution.append({

            "supply_station_id": source,

            "supply_station_name":
                nearest["supply_station_name"],

            "demand_station_id": destination,

            "demand_station_name":
                nearest["demand_station_name"],

            "bikes_moved": amount,

            "distance_km": distance,

            "bike_km":
                amount * distance

        })


        # Update remaining quantities
        remaining_supply[source] -= amount

        required -= amount


        # Remove exhausted station
        if remaining_supply[source] <= 0:

            available.remove(source)


# ============================================================
# CREATE RESULT
# ============================================================

solution_df = pd.DataFrame(solution)


# ============================================================
# SAVE
# ============================================================

solution_df.to_csv(
    OUTPUT_FILE,
    index=False
)


# ============================================================
# SUMMARY
# ============================================================

total_bikes = (
    solution_df["bikes_moved"].sum()
)

total_distance = (
    solution_df["bike_km"].sum()
)


print("\n" + "=" * 60)
print("GREEDY BASELINE RESULTS")
print("=" * 60)

print(
    "Routes used:",
    len(solution_df)
)

print(
    "Total bikes reallocated:",
    round(total_bikes, 2)
)

print(
    "Total transportation distance:",
    round(total_distance, 2),
    "bike-km"
)


print("\nTop 20 baseline routes:")

print(
    solution_df
    .sort_values(
        "bike_km",
        ascending=False
    )
    .head(20)
    .to_string(index=False)
)


print("\nSaved:")
print(OUTPUT_FILE)