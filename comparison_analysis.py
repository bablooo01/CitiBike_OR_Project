import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt


# ============================================================
# PATHS
# ============================================================

DATA_DIR = Path("data/processed")

INPUT_FILE = DATA_DIR / "optimization_comparison.csv"

FINAL_FILE = DATA_DIR / "final_optimization_analysis.csv"

DISTANCE_PLOT = DATA_DIR / "transportation_distance_comparison.png"

IMPROVEMENT_PLOT = DATA_DIR / "improvement_vs_greedy.png"

ROUTES_PLOT = DATA_DIR / "routes_comparison.png"


# ============================================================
# LOAD DATA
# ============================================================

print("=" * 70)
print("FINAL OPTIMIZATION COMPARISON ANALYSIS")
print("=" * 70)

if not INPUT_FILE.exists():

    raise FileNotFoundError(
        f"Comparison file not found:\n{INPUT_FILE}\n"
        "Run comparison.py first."
    )


comparison = pd.read_csv(INPUT_FILE)


print("\nLoaded comparison data:")

print(
    comparison.to_string(
        index=False
    )
)


# ============================================================
# CHECK METHODS
# ============================================================

expected_methods = {
    "Greedy Baseline",
    "Transportation LP",
    "Fixed-Charge Integer"
}

actual_methods = set(
    comparison["method"].tolist()
)

missing_methods = expected_methods - actual_methods

if missing_methods:

    raise ValueError(
        f"Missing expected methods: {missing_methods}"
    )


# Remove any accidental extra methods.
comparison = comparison[
    comparison["method"].isin(expected_methods)
].copy()


# ============================================================
# GREEDY BASELINE
# ============================================================

greedy_row = comparison[
    comparison["method"] == "Greedy Baseline"
].iloc[0]

greedy_distance = float(
    greedy_row["transportation_bike_km"]
)


# ============================================================
# DISTANCE REDUCTION
# ============================================================

comparison["distance_reduction_bike_km"] = (
    greedy_distance
    - comparison["transportation_bike_km"]
)


# ============================================================
# ADD RESULT CATEGORY
# ============================================================

comparison["result_type"] = comparison["method"].apply(
    lambda x:
        "Benchmark"
        if x == "Greedy Baseline"
        else "OR Optimization"
)


# ============================================================
# ROUND VALUES
# ============================================================

comparison["transportation_bike_km"] = (
    comparison["transportation_bike_km"].round(2)
)

comparison["improvement_vs_greedy_%"] = (
    comparison["improvement_vs_greedy_%"].round(2)
)

comparison["distance_reduction_bike_km"] = (
    comparison["distance_reduction_bike_km"].round(2)
)


# ============================================================
# DISPLAY FINAL COMPARISON
# ============================================================

print("\n" + "=" * 70)
print("FINAL COMPARISON")
print("=" * 70)

print(
    comparison[
        [
            "method",
            "bikes_reallocated",
            "routes_used",
            "transportation_bike_km",
            "improvement_vs_greedy_%",
            "distance_reduction_bike_km",
            "result_type"
        ]
    ].to_string(index=False)
)


# ============================================================
# BEST TRANSPORTATION RESULT
# ============================================================

optimization_only = comparison[
    comparison["method"] != "Greedy Baseline"
]

best_transportation = optimization_only.loc[
    optimization_only["transportation_bike_km"].idxmin()
]


# ============================================================
# BEST ROUTE-EFFICIENCY RESULT
# ============================================================

best_routes = optimization_only.loc[
    optimization_only["routes_used"].idxmin()
]


print("\n" + "=" * 70)
print("BEST TRANSPORTATION RESULT")
print("=" * 70)

print(
    "Method:",
    best_transportation["method"]
)

print(
    "Transportation distance:",
    best_transportation["transportation_bike_km"],
    "bike-km"
)

print(
    "Improvement over greedy:",
    best_transportation["improvement_vs_greedy_%"],
    "%"
)


print("\n" + "=" * 70)
print("BEST ROUTE-EFFICIENCY RESULT")
print("=" * 70)

print(
    "Method:",
    best_routes["method"]
)

print(
    "Routes used:",
    int(best_routes["routes_used"])
)


# ============================================================
# SAVE FINAL ANALYSIS
# ============================================================

comparison.to_csv(
    FINAL_FILE,
    index=False
)


# ============================================================
# PLOT 1: TRANSPORTATION DISTANCE
# ============================================================

plt.figure(figsize=(9, 6))

plt.bar(
    comparison["method"],
    comparison["transportation_bike_km"]
)

plt.ylabel("Transportation Distance (bike-km)")
plt.xlabel("Method")
plt.title(
    "Transportation Distance Comparison"
)

plt.xticks(rotation=15)
plt.tight_layout()

plt.savefig(
    DISTANCE_PLOT,
    dpi=300
)

plt.close()


# ============================================================
# PLOT 2: IMPROVEMENT
# ============================================================

plt.figure(figsize=(9, 6))

plt.bar(
    comparison["method"],
    comparison["improvement_vs_greedy_%"]
)

plt.ylabel("Improvement vs Greedy (%)")
plt.xlabel("Method")
plt.title(
    "Improvement over Greedy Baseline"
)

plt.xticks(rotation=15)
plt.tight_layout()

plt.savefig(
    IMPROVEMENT_PLOT,
    dpi=300
)

plt.close()


# ============================================================
# PLOT 3: ROUTES USED
# ============================================================

plt.figure(figsize=(9, 6))

plt.bar(
    comparison["method"],
    comparison["routes_used"]
)

plt.ylabel("Number of Active Routes")
plt.xlabel("Method")
plt.title(
    "Number of Routes Used"
)

plt.xticks(rotation=15)
plt.tight_layout()

plt.savefig(
    ROUTES_PLOT,
    dpi=300
)

plt.close()


# ============================================================
# FINAL OUTPUT
# ============================================================

print("\n" + "=" * 70)
print("FILES GENERATED")
print("=" * 70)

print(FINAL_FILE)
print(DISTANCE_PLOT)
print(IMPROVEMENT_PLOT)
print(ROUTES_PLOT)

print("\n" + "=" * 70)
print("FINAL ANALYSIS COMPLETED SUCCESSFULLY")
print("=" * 70)