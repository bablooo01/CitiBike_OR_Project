import pandas as pd
from pathlib import Path


# ============================================================
# PATHS
# ============================================================

DATA_DIR = Path("data/processed")

GREEDY_FILE = DATA_DIR / "greedy_baseline_solution.csv"
LP_FILE = DATA_DIR / "transportation_lp_solution.csv"
INTEGER_FILE = DATA_DIR / "integer_optimization_solution.csv"

OUTPUT_FILE = DATA_DIR / "optimization_comparison.csv"


# ============================================================
# HELPER FUNCTION
# ============================================================

def calculate_solution_metrics(file_path):
    """
    Load a solution CSV and calculate the main performance metrics.
    """

    df = pd.read_csv(file_path)

    if df.empty:
        raise ValueError(f"Solution file is empty: {file_path}")

    required_columns = [
        "bikes_moved",
        "distance_km",
        "bike_km"
    ]

    for column in required_columns:
        if column not in df.columns:
            raise ValueError(
                f"Missing column '{column}' in {file_path}"
            )

    total_bikes = int(round(df["bikes_moved"].sum()))

    total_bike_km = float(df["bike_km"].sum())

    routes_used = int((df["bikes_moved"] > 0).sum())

    return {
        "bikes_reallocated": total_bikes,
        "routes_used": routes_used,
        "transportation_bike_km": total_bike_km
    }


# ============================================================
# MAIN
# ============================================================

print("=" * 60)
print("LOADING OPTIMIZATION RESULTS")
print("=" * 60)


# ------------------------------------------------------------
# Check files
# ------------------------------------------------------------

required_files = [
    GREEDY_FILE,
    LP_FILE,
    INTEGER_FILE
]

for file_path in required_files:

    if not file_path.exists():

        raise FileNotFoundError(
            f"\nRequired file not found:\n{file_path}\n"
            "Please run the corresponding optimization script first."
        )


# ============================================================
# CALCULATE METRICS
# ============================================================

greedy = calculate_solution_metrics(GREEDY_FILE)

lp = calculate_solution_metrics(LP_FILE)

integer = calculate_solution_metrics(INTEGER_FILE)


# ============================================================
# GREEDY BASELINE
# ============================================================

greedy_distance = greedy["transportation_bike_km"]


# ============================================================
# IMPROVEMENT CALCULATIONS
# ============================================================

lp_improvement = (
    (greedy_distance - lp["transportation_bike_km"])
    / greedy_distance
    * 100
)

integer_improvement = (
    (greedy_distance - integer["transportation_bike_km"])
    / greedy_distance
    * 100
)


# ============================================================
# COMPARISON TABLE
# ============================================================

comparison = pd.DataFrame([

    {
        "method": "Greedy Baseline",
        "bikes_reallocated":
            greedy["bikes_reallocated"],
        "routes_used":
            greedy["routes_used"],
        "transportation_bike_km":
            greedy["transportation_bike_km"],
        "improvement_vs_greedy_%":
            0.0
    },

    {
        "method": "Transportation LP",
        "bikes_reallocated":
            lp["bikes_reallocated"],
        "routes_used":
            lp["routes_used"],
        "transportation_bike_km":
            lp["transportation_bike_km"],
        "improvement_vs_greedy_%":
            lp_improvement
    },

    {
        "method": "Fixed-Charge Integer",
        "bikes_reallocated":
            integer["bikes_reallocated"],
        "routes_used":
            integer["routes_used"],
        "transportation_bike_km":
            integer["transportation_bike_km"],
        "improvement_vs_greedy_%":
            integer_improvement
    }

])


# ============================================================
# DISPLAY
# ============================================================

print("\n" + "=" * 60)
print("OPTIMIZATION COMPARISON")
print("=" * 60)

print(
    comparison.to_string(
        index=False,
        formatters={
            "transportation_bike_km":
                "{:.2f}".format,
            "improvement_vs_greedy_%":
                "{:.2f}".format
        }
    )
)


# ============================================================
# BEST TRANSPORTATION RESULT
# ============================================================

optimization_results = comparison[
    comparison["method"] != "Greedy Baseline"
]

best_transportation = optimization_results.loc[
    optimization_results["transportation_bike_km"].idxmin()
]


# ============================================================
# BEST ROUTE-EFFICIENCY RESULT
# ============================================================

best_route_efficiency = optimization_results.loc[
    optimization_results["routes_used"].idxmin()
]


print("\n" + "=" * 60)
print("BEST TRANSPORTATION RESULT")
print("=" * 60)

print(
    "Method:",
    best_transportation["method"]
)

print(
    "Transportation distance:",
    round(
        best_transportation["transportation_bike_km"],
        2
    ),
    "bike-km"
)

print(
    "Routes used:",
    int(best_transportation["routes_used"])
)

print(
    "Improvement over greedy:",
    round(
        best_transportation["improvement_vs_greedy_%"],
        2
    ),
    "%"
)


print("\n" + "=" * 60)
print("BEST ROUTE-EFFICIENCY RESULT")
print("=" * 60)

print(
    "Method:",
    best_route_efficiency["method"]
)

print(
    "Routes used:",
    int(best_route_efficiency["routes_used"])
)

print(
    "Transportation distance:",
    round(
        best_route_efficiency["transportation_bike_km"],
        2
    ),
    "bike-km"
)


# ============================================================
# SAVE
# ============================================================

comparison.to_csv(
    OUTPUT_FILE,
    index=False
)

print("\nSaved:")
print(OUTPUT_FILE)

print("\nComparison completed successfully.")