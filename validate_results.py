import pandas as pd
from pathlib import Path


# ============================================================
# PATHS
# ============================================================

DATA_DIR = Path("data/processed")

SUPPLY_FILE = DATA_DIR / "optimization_supply.csv"
DEMAND_FILE = DATA_DIR / "optimization_demand.csv"

GREEDY_FILE = DATA_DIR / "greedy_baseline_solution.csv"
LP_FILE = DATA_DIR / "transportation_lp_solution.csv"
INTEGER_FILE = DATA_DIR / "integer_optimization_solution.csv"

OUTPUT_FILE = DATA_DIR / "optimization_validation_report.csv"


# ============================================================
# LOAD SUPPLY / DEMAND
# ============================================================

print("=" * 70)
print("CITIBIKE OPTIMIZATION VALIDATION")
print("=" * 70)

print("\nLoading supply and demand data...")

supply = pd.read_csv(SUPPLY_FILE)
demand = pd.read_csv(DEMAND_FILE)


# ============================================================
# TOTAL SUPPLY / DEMAND
# ============================================================

total_supply = int(
    supply["supply"].sum()
)

total_demand = int(
    demand["demand"].sum()
)


print(
    "Total available supply :",
    total_supply
)

print(
    "Total required demand  :",
    total_demand
)


balance_pass = (
    total_supply == total_demand
)


print(
    "Balance check            :",
    "PASS" if balance_pass else "FAIL"
)


# ============================================================
# VALIDATION FUNCTION
# ============================================================

def validate_solution(
    name,
    file_path
):

    print("\n" + "=" * 70)
    print(name)
    print("=" * 70)

    if not file_path.exists():

        print(
            f"ERROR: File not found: {file_path}"
        )

        return {
            "method": name,
            "bikes_moved": 0,
            "routes_used": 0,
            "transportation_bike_km": 0,
            "unmet_demand": None,
            "supply_check": "FAIL",
            "demand_check": "FAIL",
            "integer_check": "FAIL",
            "bike_km_check": "FAIL",
            "overall_validation": "FAIL"
        }


    df = pd.read_csv(file_path)


    # --------------------------------------------------------
    # Required columns
    # --------------------------------------------------------

    required_columns = [
        "supply_station_id",
        "demand_station_id",
        "bikes_moved",
        "distance_km",
        "bike_km"
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:

        raise ValueError(
            f"{name} is missing columns: "
            f"{missing_columns}"
        )


    # --------------------------------------------------------
    # Total bikes
    # --------------------------------------------------------

    total_bikes = int(
        round(df["bikes_moved"].sum())
    )

    total_bikes_check = (
        total_bikes == total_demand
    )


    print(
        "Total bikes moved       :",
        total_bikes
    )

    print(
        "Total bikes check       :",
        "PASS"
        if total_bikes_check
        else "FAIL"
    )


    # --------------------------------------------------------
    # Negative movement
    # --------------------------------------------------------

    negative_check = (
        (df["bikes_moved"] >= 0).all()
    )

    print(
        "Negative movement check :",
        "PASS"
        if negative_check
        else "FAIL"
    )


    # --------------------------------------------------------
    # Integer movement
    # --------------------------------------------------------

    integer_check = (
        df["bikes_moved"]
        .apply(
            lambda x: float(x).is_integer()
        )
        .all()
    )

    print(
        "Integer movement check  :",
        "PASS"
        if integer_check
        else "FAIL"
    )


    # --------------------------------------------------------
    # Supply constraints
    # --------------------------------------------------------

    outgoing = (
        df.groupby(
            "supply_station_id"
        )["bikes_moved"]
        .sum()
    )

    supply_check = True

    for station_id, moved in outgoing.items():

        if station_id not in set(
            supply["station_id"]
        ):

            supply_check = False
            break

        available = supply.loc[
            supply["station_id"] == station_id,
            "supply"
        ].iloc[0]

        if moved > available + 1e-6:

            supply_check = False
            break


    print(
        "Supply constraints      :",
        "PASS"
        if supply_check
        else "FAIL"
    )


    # --------------------------------------------------------
    # Demand constraints
    # --------------------------------------------------------

    incoming = (
        df.groupby(
            "demand_station_id"
        )["bikes_moved"]
        .sum()
    )

    demand_check = True

    for station_id, required in zip(
        demand["station_id"],
        demand["demand"]
    ):

        received = incoming.get(
            station_id,
            0
        )

        if received + 1e-6 < required:

            demand_check = False
            break


    print(
        "Demand constraints      :",
        "PASS"
        if demand_check
        else "FAIL"
    )


    # --------------------------------------------------------
    # Unmet demand
    # --------------------------------------------------------

    unmet_demand = 0

    for station_id, required in zip(
        demand["station_id"],
        demand["demand"]
    ):

        received = incoming.get(
            station_id,
            0
        )

        unmet_demand += max(
            0,
            required - received
        )


    unmet_check = (
        unmet_demand <= 1e-6
    )


    print(
        "Unmet demand            :",
        int(round(unmet_demand))
    )

    print(
        "Unmet demand check      :",
        "PASS"
        if unmet_check
        else "FAIL"
    )


    # --------------------------------------------------------
    # Bike-km calculation
    # --------------------------------------------------------

    calculated_bike_km = (
        df["bikes_moved"]
        * df["distance_km"]
    ).sum()

    reported_bike_km = (
        df["bike_km"].sum()
    )

    bike_km_check = (
        abs(
            calculated_bike_km
            - reported_bike_km
        )
        <= 0.01
    )


    print(
        "Calculated bike-km     :",
        round(calculated_bike_km, 2)
    )

    print(
        "Reported bike-km       :",
        round(reported_bike_km, 2)
    )

    print(
        "Bike-km calculation     :",
        "PASS"
        if bike_km_check
        else "FAIL"
    )


    # --------------------------------------------------------
    # Routes
    # --------------------------------------------------------

    routes_used = int(
        (df["bikes_moved"] > 0).sum()
    )


    print(
        "Routes used             :",
        routes_used
    )


    # --------------------------------------------------------
    # Distance validity
    # --------------------------------------------------------

    distance_validity = (
        (df["distance_km"] >= 0).all()
    )

    print(
        "Distance validity       :",
        "PASS"
        if distance_validity
        else "FAIL"
    )


    # --------------------------------------------------------
    # Overall validation
    # --------------------------------------------------------

    overall_pass = all([
        total_bikes_check,
        negative_check,
        integer_check,
        supply_check,
        demand_check,
        unmet_check,
        bike_km_check,
        distance_validity
    ])


    print("\nOverall validation      :")

    if overall_pass:

        print(
            "PASS - Solution is feasible "
            "and internally consistent."
        )

    else:

        print(
            "FAIL - One or more validation "
            "checks failed."
        )


    return {
        "method": name,
        "bikes_moved": total_bikes,
        "routes_used": routes_used,
        "transportation_bike_km":
            round(reported_bike_km, 2),
        "unmet_demand":
            round(unmet_demand, 2),
        "supply_check":
            "PASS" if supply_check else "FAIL",
        "demand_check":
            "PASS" if demand_check else "FAIL",
        "integer_check":
            "PASS" if integer_check else "FAIL",
        "bike_km_check":
            "PASS" if bike_km_check else "FAIL",
        "overall_validation":
            "PASS" if overall_pass else "FAIL"
    }


# ============================================================
# VALIDATE THREE RESULTS
# ============================================================

results = []


results.append(
    validate_solution(
        "GREEDY BASELINE",
        GREEDY_FILE
    )
)


results.append(
    validate_solution(
        "TRANSPORTATION LP",
        LP_FILE
    )
)


results.append(
    validate_solution(
        "FIXED-CHARGE INTEGER",
        INTEGER_FILE
    )
)


# ============================================================
# FINAL SUMMARY
# ============================================================

validation_df = pd.DataFrame(results)


print("\n" + "=" * 70)
print("FINAL VALIDATION SUMMARY")
print("=" * 70)

print(
    validation_df.to_string(
        index=False
    )
)


# ============================================================
# SAVE
# ============================================================

validation_df.to_csv(
    OUTPUT_FILE,
    index=False
)


print("\nValidation report saved:")
print(OUTPUT_FILE)


# ============================================================
# FINAL CHECK
# ============================================================

all_pass = (
    validation_df["overall_validation"]
    == "PASS"
).all()


print("\n" + "=" * 70)

if all_pass:

    print(
        "ALL OPTIMIZATION SOLUTIONS "
        "PASSED VALIDATION"
    )

else:

    print(
        "WARNING: ONE OR MORE SOLUTIONS "
        "FAILED VALIDATION"
    )

print("=" * 70)