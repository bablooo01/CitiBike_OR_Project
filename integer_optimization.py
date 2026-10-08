import pandas as pd
import pulp
from pathlib import Path
import re


# ============================================================
# PATHS
# ============================================================

DATA_DIR = Path("data/processed")

SUPPLY_FILE = DATA_DIR / "optimization_supply.csv"
DEMAND_FILE = DATA_DIR / "optimization_demand.csv"
COST_FILE = DATA_DIR / "transportation_cost_matrix.csv"

OUTPUT_FILE = DATA_DIR / "integer_optimization_solution.csv"
LOG_FILE = DATA_DIR / "integer_optimization_cbc.log"


# ============================================================
# PARAMETERS
# ============================================================

# Maximum number of bikes that can be assigned to one
# source -> destination transfer lane.
ROUTE_CAPACITY = 1000

# Fixed cost/penalty for activating a transfer lane.
ROUTE_PENALTY = 100

# Maximum CBC solving time in seconds.
TIME_LIMIT = 300


# ============================================================
# FUNCTION: READ CBC LOG
# ============================================================

def read_cbc_status(log_file):
    """
    Reads the CBC log and determines whether the solver
    proved optimality or stopped because of the time limit.
    """

    result = {
        "time_limit": False,
        "optimal": False,
        "objective": None,
        "lower_bound": None,
        "gap": None
    }

    if not log_file.exists():
        return result

    text = log_file.read_text(
        encoding="utf-8",
        errors="ignore"
    )

    # Detect time-limit termination
    if "Result - Stopped on time limit" in text:
        result["time_limit"] = True

    # Detect proven optimal solution
    if "Result - Optimal solution found" in text:
        result["optimal"] = True

    # Objective value
    match = re.search(
        r"Objective value:\s*([-+]?\d*\.?\d+)",
        text
    )

    if match:
        result["objective"] = float(match.group(1))

    # Lower bound
    match = re.search(
        r"Lower bound:\s*([-+]?\d*\.?\d+)",
        text
    )

    if match:
        result["lower_bound"] = float(match.group(1))

    # Gap
    match = re.search(
        r"Gap:\s*([-+]?\d*\.?\d+)",
        text
    )

    if match:
        result["gap"] = float(match.group(1))

    return result


# ============================================================
# LOAD DATA
# ============================================================

print("Loading optimization data...")

if not SUPPLY_FILE.exists():
    raise FileNotFoundError(
        f"Supply file not found: {SUPPLY_FILE}"
    )

if not DEMAND_FILE.exists():
    raise FileNotFoundError(
        f"Demand file not found: {DEMAND_FILE}"
    )

if not COST_FILE.exists():
    raise FileNotFoundError(
        f"Cost matrix file not found: {COST_FILE}"
    )

supply = pd.read_csv(SUPPLY_FILE)
demand = pd.read_csv(DEMAND_FILE)
cost = pd.read_csv(COST_FILE)

print("Supply stations:", len(supply))
print("Demand stations:", len(demand))
print("Possible routes:", len(cost))


# ============================================================
# SETS
# ============================================================

sources = supply["station_id"].tolist()
destinations = demand["station_id"].tolist()


# ============================================================
# SUPPLY / DEMAND VALUES
# ============================================================

supply_values = dict(
    zip(
        supply["station_id"],
        supply["supply"].astype(int)
    )
)

demand_values = dict(
    zip(
        demand["station_id"],
        demand["demand"].astype(int)
    )
)


# ============================================================
# STATION NAMES
# ============================================================

supply_names = dict(
    zip(
        supply["station_id"],
        supply["station_name"]
    )
)

demand_names = dict(
    zip(
        demand["station_id"],
        demand["station_name"]
    )
)


# ============================================================
# DISTANCE DATA
# ============================================================

distance = {}

for _, row in cost.iterrows():

    i = row["supply_station_id"]
    j = row["demand_station_id"]

    distance[i, j] = float(row["distance_km"])


routes = list(distance.keys())


# ============================================================
# TOTAL SUPPLY / DEMAND CHECK
# ============================================================

total_supply_available = sum(
    supply_values.values()
)

total_demand_required = sum(
    demand_values.values()
)

print("\n============================================================")
print("MODEL BALANCE CHECK")
print("============================================================")

print(
    "Total available supply:",
    total_supply_available
)

print(
    "Total required demand:",
    total_demand_required
)

if total_supply_available < total_demand_required:

    raise ValueError(
        "Model cannot satisfy all demand because total supply "
        "is smaller than total demand."
    )

print("Supply is sufficient for the demand.")


# ============================================================
# CREATE MIXED INTEGER PROGRAM
# ============================================================

model = pulp.LpProblem(
    "CitiBike_Fixed_Charge_Integer_Rebalancing",
    pulp.LpMinimize
)


# ============================================================
# DECISION VARIABLE
#
# x[i,j] = INTEGER NUMBER OF BIKES MOVED
# ============================================================

x = {}

for i, j in routes:

    x[i, j] = pulp.LpVariable(
        f"x_{i}_{j}",
        lowBound=0,
        cat=pulp.LpInteger
    )


# ============================================================
# DECISION VARIABLE
#
# y[i,j] = BINARY ROUTE ACTIVATION
# ============================================================

y = {}

for i, j in routes:

    y[i, j] = pulp.LpVariable(
        f"y_{i}_{j}",
        cat=pulp.LpBinary
    )


# ============================================================
# OBJECTIVE
#
# Minimize:
#
# transportation distance
# +
# fixed route activation penalty
# ============================================================

model += pulp.lpSum(
    distance[i, j] * x[i, j]
    + ROUTE_PENALTY * y[i, j]
    for i, j in routes
)


# ============================================================
# SUPPLY CONSTRAINTS
#
# Bikes leaving a surplus station cannot exceed
# the available supply.
# ============================================================

for i in sources:

    outgoing = [
        x[i, j]
        for ii, j in routes
        if ii == i
    ]

    model += (
        pulp.lpSum(outgoing)
        <= supply_values[i]
    ), f"Supply_{i}"


# ============================================================
# DEMAND CONSTRAINTS
#
# Each deficit station must receive at least
# its required demand.
# ============================================================

for j in destinations:

    incoming = [
        x[i, j]
        for i, jj in routes
        if jj == j
    ]

    model += (
        pulp.lpSum(incoming)
        >= demand_values[j]
    ), f"Demand_{j}"


# ============================================================
# FIXED-CHARGE / ROUTE CAPACITY CONSTRAINT
#
# x[i,j] <= ROUTE_CAPACITY * y[i,j]
#
# If y = 0 -> x = 0
# If y = 1 -> x <= ROUTE_CAPACITY
# ============================================================

for i, j in routes:

    model += (
        x[i, j]
        <= ROUTE_CAPACITY * y[i, j]
    ), f"RouteCapacity_{i}_{j}"


# ============================================================
# SOLVE
# ============================================================

print("\n" + "=" * 60)
print("SOLVING FIXED-CHARGE INTEGER REBALANCING MODEL")
print("=" * 60)

print("Route capacity:", ROUTE_CAPACITY)
print("Route activation penalty:", ROUTE_PENALTY)
print("Candidate routes:", len(routes))
print("Time limit:", TIME_LIMIT, "seconds")


solver = pulp.PULP_CBC_CMD(
    msg=True,
    timeLimit=TIME_LIMIT,
    logPath=str(LOG_FILE)
)


model.solve(solver)


# ============================================================
# READ ACTUAL CBC RESULT
# ============================================================

cbc_result = read_cbc_status(LOG_FILE)


print("\n" + "=" * 60)
print("SOLVER RESULT")
print("=" * 60)


if cbc_result["time_limit"]:

    print(
        "Best feasible solution found within",
        TIME_LIMIT,
        "seconds."
    )

    print(
        "CBC stopped because the time limit was reached."
    )

    print(
        "Mathematical optimality was NOT proven."
    )

elif cbc_result["optimal"]:

    print(
        "Optimal solution found."
    )

else:

    print(
        "CBC termination condition could not be determined "
        "from the log."
    )


# ============================================================
# CHECK SOLUTION AVAILABILITY
# ============================================================

solution_values = []

for i, j in routes:

    value = x[i, j].value()

    if value is not None:

        solution_values.append(value)


if len(solution_values) == 0:

    print(
        "\nNo feasible solution was produced."
    )

    raise SystemExit


# ============================================================
# EXTRACT SOLUTION
# ============================================================

solution = []

for i, j in routes:

    bikes = x[i, j].value()
    route_used = y[i, j].value()

    if bikes is None:
        continue

    if bikes > 0:

        bikes_int = int(round(bikes))

        activated_int = (
            int(round(route_used))
            if route_used is not None
            else 0
        )

        solution.append({

            "supply_station_id": i,

            "supply_station_name":
                supply_names[i],

            "demand_station_id": j,

            "demand_station_name":
                demand_names[j],

            "bikes_moved":
                bikes_int,

            "distance_km":
                distance[i, j],

            "bike_km":
                bikes_int * distance[i, j],

            "route_activated":
                activated_int

        })


# ============================================================
# CHECK SOLUTION
# ============================================================

if len(solution) == 0:

    print(
        "No positive bike movements were found."
    )

    raise SystemExit


solution_df = pd.DataFrame(solution)


# ============================================================
# METRICS
# ============================================================

total_bikes = int(
    solution_df["bikes_moved"].sum()
)

transport_distance = float(
    solution_df["bike_km"].sum()
)

routes_used = int(
    (solution_df["route_activated"] > 0).sum()
)

activation_cost = (
    routes_used * ROUTE_PENALTY
)

total_objective = (
    transport_distance
    + activation_cost
)


# ============================================================
# INTEGER VALIDATION
# ============================================================

integer_check = all(
    float(value).is_integer()
    for value in solution_df["bikes_moved"]
)


# ============================================================
# SUPPLY VALIDATION
# ============================================================

supply_check = True

for i in sources:

    moved = solution_df.loc[
        solution_df["supply_station_id"] == i,
        "bikes_moved"
    ].sum()

    if moved > supply_values[i]:

        supply_check = False


# ============================================================
# DEMAND VALIDATION
# ============================================================

demand_check = True

demand_received = {}

for j in destinations:

    received = solution_df.loc[
        solution_df["demand_station_id"] == j,
        "bikes_moved"
    ].sum()

    demand_received[j] = received

    if received < demand_values[j]:

        demand_check = False


# ============================================================
# SAVE SOLUTION
# ============================================================

solution_df.to_csv(
    OUTPUT_FILE,
    index=False
)


# ============================================================
# RESULTS
# ============================================================

print("\n" + "=" * 60)
print("FIXED-CHARGE INTEGER OPTIMIZATION RESULTS")
print("=" * 60)

print(
    "Routes used:",
    routes_used
)

print(
    "Total bikes reallocated:",
    total_bikes
)

print(
    "Transportation distance:",
    round(
        transport_distance,
        2
    ),
    "bike-km"
)

print(
    "Route activation cost:",
    round(
        activation_cost,
        2
    )
)

print(
    "Total objective value:",
    round(
        total_objective,
        2
    )
)

print(
    "All bike movements integer:",
    integer_check
)

print(
    "Supply constraints satisfied:",
    supply_check
)

print(
    "Demand constraints satisfied:",
    demand_check
)


# ============================================================
# CBC OBJECTIVE / GAP
# ============================================================

print("\nCBC SOLVER INFORMATION")

if cbc_result["objective"] is not None:

    print(
        "CBC objective:",
        round(
            cbc_result["objective"],
            4
        )
    )

if cbc_result["lower_bound"] is not None:

    print(
        "CBC lower bound:",
        round(
            cbc_result["lower_bound"],
            4
        )
    )

if cbc_result["gap"] is not None:

    print(
        "CBC optimality gap:",
        f"{cbc_result['gap'] * 100:.2f}%"
    )


# ============================================================
# TOP ROUTES
# ============================================================

print("\nTop 20 integer optimization routes:")

print(
    solution_df
    .sort_values(
        "bike_km",
        ascending=False
    )
    .head(20)
    .to_string(index=False)
)


# ============================================================
# OUTPUT
# ============================================================

print("\nSaved:")
print(OUTPUT_FILE)

print("\nCBC log:")
print(LOG_FILE)

print("\nInteger optimization completed successfully.")