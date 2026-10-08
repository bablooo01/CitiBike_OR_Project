import pandas as pd
import pulp
from pathlib import Path


# ============================================================
# PATHS
# ============================================================

DATA_DIR = Path("data/processed")

SUPPLY_FILE = DATA_DIR / "optimization_supply.csv"
DEMAND_FILE = DATA_DIR / "optimization_demand.csv"
COST_FILE = DATA_DIR / "transportation_cost_matrix.csv"

OUTPUT_FILE = DATA_DIR / "transportation_lp_solution.csv"


# ============================================================
# LOAD DATA
# ============================================================

print("Loading optimization data...")

supply = pd.read_csv(SUPPLY_FILE)
demand = pd.read_csv(DEMAND_FILE)
cost = pd.read_csv(COST_FILE)


print("Supply stations:", len(supply))
print("Demand stations:", len(demand))
print("Routes:", len(cost))


# ============================================================
# CREATE DICTIONARIES
# ============================================================

supply_values = dict(
    zip(
        supply["station_id"],
        supply["supply"]
    )
)


demand_values = dict(
    zip(
        demand["station_id"],
        demand["demand"]
    )
)


# ============================================================
# SETS
# ============================================================

sources = supply["station_id"].tolist()

destinations = demand["station_id"].tolist()


# ============================================================
# CREATE TRANSPORTATION LP
# ============================================================

model = pulp.LpProblem(
    "CitiBike_Transportation_Rebalancing",
    pulp.LpMinimize
)


# ============================================================
# DECISION VARIABLES
# ============================================================

x = {}

for i in sources:

    for j in destinations:

        x[i, j] = pulp.LpVariable(
            f"x_{i}_{j}",
            lowBound=0,
            cat="Continuous"
        )


# ============================================================
# OBJECTIVE FUNCTION
# ============================================================

model += pulp.lpSum(
    cost[
        (
            cost["supply_station_id"] == i
        )
        &
        (
            cost["demand_station_id"] == j
        )
    ]["distance_km"].iloc[0]
    * x[i, j]

    for i in sources

    for j in destinations
)


# ============================================================
# SUPPLY CONSTRAINTS
# ============================================================

for i in sources:

    model += (
        pulp.lpSum(
            x[i, j]
            for j in destinations
        )
        <= supply_values[i]
    ), f"Supply_{i}"


# ============================================================
# DEMAND CONSTRAINTS
# ============================================================

for j in destinations:

    model += (
        pulp.lpSum(
            x[i, j]
            for i in sources
        )
        >= demand_values[j]
    ), f"Demand_{j}"


# ============================================================
# SOLVE
# ============================================================

print("\n" + "=" * 60)
print("SOLVING TRANSPORTATION LP")
print("=" * 60)

solver = pulp.PULP_CBC_CMD(
    msg=True
)

model.solve(solver)


# ============================================================
# STATUS
# ============================================================

print("\nSolver status:")

print(
    pulp.LpStatus[
        model.status
    ]
)


# ============================================================
# OBJECTIVE
# ============================================================

print("\nOptimal transportation distance:")

print(
    round(
        pulp.value(
            model.objective
        ),
        2
    ),
    "bike-km"
)


# ============================================================
# EXTRACT SOLUTION
# ============================================================

solution = []


for i in sources:

    for j in destinations:

        amount = x[i, j].value()

        if amount is not None and amount > 0.0001:

            distance = cost[
                (
                    cost["supply_station_id"] == i
                )
                &
                (
                    cost["demand_station_id"] == j
                )
            ]["distance_km"].iloc[0]


            solution.append({

                "supply_station_id": i,

                "supply_station_name":
                    supply.loc[
                        supply["station_id"] == i,
                        "station_name"
                    ].iloc[0],

                "demand_station_id": j,

                "demand_station_name":
                    demand.loc[
                        demand["station_id"] == j,
                        "station_name"
                    ].iloc[0],

                "bikes_moved": amount,

                "distance_km": distance,

                "bike_km":
                    amount * distance

            })


# ============================================================
# SOLUTION DATAFRAME
# ============================================================

solution_df = pd.DataFrame(
    solution
)


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

print("\n" + "=" * 60)
print("OPTIMIZATION RESULTS")
print("=" * 60)

print(
    "Routes used:",
    len(solution_df)
)

print(
    "Total bikes reallocated:",
    round(
        solution_df["bikes_moved"].sum(),
        2
    )
)

print(
    "Total transportation distance:",
    round(
        solution_df["bike_km"].sum(),
        2
    ),
    "bike-km"
)


print("\nTop 20 selected routes:")

print(
    solution_df
    .sort_values(
        "bike_km",
        ascending=False
    )
    .head(20)
    .to_string(
        index=False
    )
)


print("\nSaved solution:")

print(OUTPUT_FILE)