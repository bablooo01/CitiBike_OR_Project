import pandas as pd
from pathlib import Path


# ============================================================
# PATHS
# ============================================================

INPUT_FILE = Path(
    "data/processed/evening_peak_station_demand.csv"
)

OUTPUT_DIR = Path(
    "data/processed"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# SETTINGS
# ============================================================

N_STATIONS = 30


# ============================================================
# LOAD DATA
# ============================================================

print("Loading evening peak station data...")

data = pd.read_csv(INPUT_FILE)

print(
    "Total stations:",
    len(data)
)


# ============================================================
# SELECT TOP SURPLUS STATIONS
# ============================================================

surplus = (
    data[data["net_flow"] > 0]
    .sort_values(
        "net_flow",
        ascending=False
    )
    .head(N_STATIONS)
    .copy()
)


# ============================================================
# SELECT TOP DEFICIT STATIONS
# ============================================================

deficit = (
    data[data["net_flow"] < 0]
    .sort_values(
        "net_flow",
        ascending=True
    )
    .head(N_STATIONS)
    .copy()
)


# ============================================================
# SUPPLY
# ============================================================

surplus["supply"] = (
    surplus["net_flow"]
)


# ============================================================
# DEMAND
# ============================================================

deficit["demand"] = (
    -deficit["net_flow"]
)


# ============================================================
# BALANCE TOTAL SUPPLY AND DEMAND
# ============================================================

total_supply = surplus["supply"].sum()

total_demand = deficit["demand"].sum()


print("\n" + "=" * 60)
print("INITIAL SUPPLY / DEMAND")
print("=" * 60)

print(
    "Total selected supply:",
    f"{total_supply:,.0f}"
)

print(
    "Total selected demand:",
    f"{total_demand:,.0f}"
)


# ============================================================
# BALANCING
# ============================================================

# Transportation models require
# total supply = total demand.

if total_supply > total_demand:

    difference = total_supply - total_demand

    print(
        f"\nSupply exceeds demand by {difference:,.0f}"
    )

    # Scale supply proportionally
    surplus["supply"] = (
        surplus["supply"]
        * total_demand
        / total_supply
    )

elif total_demand > total_supply:

    difference = total_demand - total_supply

    print(
        f"\nDemand exceeds supply by {difference:,.0f}"
    )

    # Scale demand proportionally
    deficit["demand"] = (
        deficit["demand"]
        * total_supply
        / total_demand
    )


# ============================================================
# ROUND SUPPLY / DEMAND
# ============================================================

surplus["supply"] = (
    surplus["supply"]
    .round()
    .astype(int)
)

deficit["demand"] = (
    deficit["demand"]
    .round()
    .astype(int)
)


# ============================================================
# FINAL BALANCE CORRECTION
# ============================================================

supply_total = surplus["supply"].sum()

demand_total = deficit["demand"].sum()

difference = supply_total - demand_total


if difference > 0:

    # Reduce largest supply
    index = surplus["supply"].idxmax()

    surplus.loc[
        index,
        "supply"
    ] -= difference


elif difference < 0:

    # Reduce largest demand
    index = deficit["demand"].idxmax()

    deficit.loc[
        index,
        "demand"
    ] += difference


# ============================================================
# FINAL CHECK
# ============================================================

supply_total = surplus["supply"].sum()

demand_total = deficit["demand"].sum()


print("\n" + "=" * 60)
print("FINAL BALANCED MODEL")
print("=" * 60)

print(
    "Supply:",
    f"{supply_total:,}"
)

print(
    "Demand:",
    f"{demand_total:,}"
)

print(
    "Balanced:",
    supply_total == demand_total
)


# ============================================================
# SAVE SUPPLY DATA
# ============================================================

surplus_file = (
    OUTPUT_DIR /
    "optimization_supply.csv"
)

surplus.to_csv(
    surplus_file,
    index=False
)


# ============================================================
# SAVE DEMAND DATA
# ============================================================

deficit_file = (
    OUTPUT_DIR /
    "optimization_demand.csv"
)

deficit.to_csv(
    deficit_file,
    index=False
)


# ============================================================
# DISPLAY
# ============================================================

print("\nTOP SUPPLY STATIONS")

print(
    surplus[
        [
            "station_id",
            "station_name",
            "latitude",
            "longitude",
            "supply"
        ]
    ]
    .to_string(index=False)
)


print("\nTOP DEMAND STATIONS")

print(
    deficit[
        [
            "station_id",
            "station_name",
            "latitude",
            "longitude",
            "demand"
        ]
    ]
    .to_string(index=False)
)


print("\nSaved:")
print(surplus_file)
print(deficit_file)