import streamlit as st
import pandas as pd
from pathlib import Path
import subprocess
import sys


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="CitiBike OR Optimization",
    page_icon="🚲",
    layout="wide"
)


# ============================================================
# PATHS
# ============================================================

PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_DIR / "data" / "processed"

SUPPLY_FILE = DATA_DIR / "optimization_supply.csv"
DEMAND_FILE = DATA_DIR / "optimization_demand.csv"
COST_FILE = DATA_DIR / "transportation_cost_matrix.csv"

GREEDY_FILE = DATA_DIR / "greedy_baseline_solution.csv"
LP_FILE = DATA_DIR / "transportation_lp_solution.csv"
INTEGER_FILE = DATA_DIR / "integer_optimization_solution.csv"

COMPARISON_FILE = DATA_DIR / "optimization_comparison.csv"
VALIDATION_FILE = DATA_DIR / "optimization_validation_report.csv"


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def load_csv(path):
    """Load CSV safely."""
    if path.exists():
        return pd.read_csv(path)
    return None


def run_script(script_name):
    """Run an existing optimization Python script."""
    script_path = PROJECT_DIR / script_name

    if not script_path.exists():
        return False, f"File not found: {script_path}"

    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            cwd=str(PROJECT_DIR),
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            return True, result.stdout

        return False, result.stdout + "\n" + result.stderr

    except Exception as e:
        return False, str(e)


# ============================================================
# TITLE
# ============================================================

st.title("🚲 CitiBike Operations Research Optimization")

st.markdown(
    """
    ### Bike Rebalancing Optimization

    This application applies Operations Research techniques to
    optimize the redistribution of CitiBike bicycles between
    supply and demand stations.
    """
)

st.divider()


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.header("Navigation")

page = st.sidebar.radio(
    "Select Section",
    [
        "Overview",
        "Dataset & Statistics",
        "Optimization",
        "Comparison",
        "Validation"
    ]
)


# ============================================================
# OVERVIEW
# ============================================================

if page == "Overview":

    st.header("Project Overview")

    st.markdown(
        """
        ### Problem Statement

        CitiBike stations may have excess bicycles at some locations
        and insufficient bicycles at other locations.

        The objective is to determine how bicycles should be
        reallocated while minimizing transportation distance.

        ### Operations Research Techniques

        This project implements two optimization techniques:

        **1. Transportation Linear Programming (LP)**

        Minimizes total transportation distance while satisfying
        supply and demand constraints.

        **2. Fixed-Charge Integer Programming**

        Extends the transportation model by considering:

        - Integer bicycle movements
        - Route activation
        - Route capacity
        - Fixed route activation cost

        ### Benchmark

        A Greedy Baseline is used as a benchmark to evaluate the
        improvement obtained through OR optimization.
        """
    )

    st.success(
        "The project satisfies the requirement of implementing "
        "at least two optimization techniques."
    )

    st.subheader("Optimization Workflow")

    st.code(
        """
CitiBike Dataset
       ↓
Data Preparation
       ↓
Supply / Demand Estimation
       ↓
Greedy Baseline
       ↓
┌─────────────────────────────┐
│ Transportation LP           │
│ Fixed-Charge Integer Model  │
└─────────────────────────────┘
       ↓
Validation
       ↓
Comparison & Analysis
       ↓
Final Decision
        """,
        language="text"
    )


# ============================================================
# DATASET & STATISTICS
# ============================================================

elif page == "Dataset & Statistics":

    st.header("📊 Dataset & Statistics")

    supply = load_csv(SUPPLY_FILE)
    demand = load_csv(DEMAND_FILE)
    cost = load_csv(COST_FILE)

    if supply is None or demand is None or cost is None:

        st.error(
            "Required optimization data files were not found."
        )

    else:

        st.subheader("Dataset Summary")

        total_supply = int(supply["supply"].sum())
        total_demand = int(demand["demand"].sum())

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "Supply Stations",
            len(supply)
        )

        col2.metric(
            "Demand Stations",
            len(demand)
        )

        col3.metric(
            "Total Supply",
            f"{total_supply:,}"
        )

        col4.metric(
            "Total Demand",
            f"{total_demand:,}"
        )

        st.divider()

        if total_supply == total_demand:
            st.success(
                f"Supply and demand are balanced: "
                f"{total_supply:,} bikes."
            )
        elif total_supply > total_demand:
            st.info(
                f"Supply exceeds demand by "
                f"{total_supply - total_demand:,} bikes."
            )
        else:
            st.warning(
                f"Demand exceeds supply by "
                f"{total_demand - total_supply:,} bikes."
            )

        # ----------------------------------------------------
        # SUPPLY DATA
        # ----------------------------------------------------

        st.subheader("Supply Stations")

        st.dataframe(
            supply,
            use_container_width=True
        )

        # ----------------------------------------------------
        # DEMAND DATA
        # ----------------------------------------------------

        st.subheader("Demand Stations")

        st.dataframe(
            demand,
            use_container_width=True
        )

        # ----------------------------------------------------
        # TRANSPORTATION COST MATRIX
        # ----------------------------------------------------

        st.subheader("Transportation Cost / Distance Data")

        st.write(
            f"Possible source-destination routes: "
            f"**{len(cost):,}**"
        )

        st.dataframe(
            cost.head(100),
            use_container_width=True
        )

        # ----------------------------------------------------
        # BASIC STATISTICS
        # ----------------------------------------------------

        st.subheader("Basic Statistics")

        stat1, stat2, stat3 = st.columns(3)

        stat1.metric(
            "Average Supply",
            round(supply["supply"].mean(), 2)
        )

        stat2.metric(
            "Average Demand",
            round(demand["demand"].mean(), 2)
        )

        if "distance_km" in cost.columns:

            stat3.metric(
                "Average Route Distance",
                f"{cost['distance_km'].mean():.2f} km"
            )


# ============================================================
# OPTIMIZATION
# ============================================================

elif page == "Optimization":

    st.header("⚙️ Optimization")

    st.markdown(
        """
        Select one of the two Operations Research optimization
        techniques implemented in this project.
        """
    )

    method = st.selectbox(
        "Choose Optimization Method",
        [
            "Transportation LP",
            "Fixed-Charge Integer Programming"
        ]
    )

    st.divider()

    if method == "Transportation LP":

        st.subheader("Transportation Linear Programming")

        st.markdown(
            """
            **Objective:** Minimize total transportation distance.

            **Constraints:**
            - Supply constraints
            - Demand constraints
            - Non-negative bike movements
            """
        )

        if st.button(
            "▶ Run Transportation LP",
            type="primary"
        ):

            with st.spinner(
                "Running Transportation LP..."
            ):

                success, output = run_script(
                    "transportation_lp.py"
                )

            if success:

                st.success(
                    "Transportation LP completed successfully."
                )

                result = load_csv(LP_FILE)

                if result is not None:

                    total_bikes = int(
                        result["bikes_moved"].sum()
                    )

                    bike_km = result["bike_km"].sum()

                    routes = len(result)

                    c1, c2, c3 = st.columns(3)

                    c1.metric(
                        "Bikes Reallocated",
                        f"{total_bikes:,}"
                    )

                    c2.metric(
                        "Transportation Distance",
                        f"{bike_km:,.2f} bike-km"
                    )

                    c3.metric(
                        "Routes Used",
                        routes
                    )

                    st.subheader("Optimization Routes")

                    st.dataframe(
                        result,
                        use_container_width=True
                    )

            else:

                st.error(
                    "Transportation LP failed."
                )

                st.code(output)

    else:

        st.subheader(
            "Fixed-Charge Integer Programming"
        )

        st.markdown(
            """
            **Objective:** Minimize transportation distance plus
            fixed route activation cost.

            **Features:**
            - Integer bicycle movements
            - Route activation variables
            - Route capacity constraints
            - Supply constraints
            - Demand constraints
            """
        )

        if st.button(
            "▶ Run Fixed-Charge Integer Optimization",
            type="primary"
        ):

            with st.spinner(
                "Running Fixed-Charge Integer Optimization..."
            ):

                success, output = run_script(
                    "integer_optimization.py"
                )

            if success:

                st.success(
                    "Fixed-Charge Integer Optimization "
                    "completed successfully."
                )

                result = load_csv(INTEGER_FILE)

                if result is not None:

                    total_bikes = int(
                        result["bikes_moved"].sum()
                    )

                    bike_km = result["bike_km"].sum()

                    routes = len(result)

                    c1, c2, c3 = st.columns(3)

                    c1.metric(
                        "Bikes Reallocated",
                        f"{total_bikes:,}"
                    )

                    c2.metric(
                        "Transportation Distance",
                        f"{bike_km:,.2f} bike-km"
                    )

                    c3.metric(
                        "Routes Used",
                        routes
                    )

                    st.subheader(
                        "Integer Optimization Routes"
                    )

                    st.dataframe(
                        result,
                        use_container_width=True
                    )

            else:

                st.error(
                    "Fixed-Charge Integer Optimization failed."
                )

                st.code(output)


# ============================================================
# COMPARISON
# ============================================================

elif page == "Comparison":

    st.header("📈 Optimization Comparison")

    comparison = load_csv(COMPARISON_FILE)

    if comparison is None:

        st.warning(
            "Comparison file not found. "
            "Run comparison.py first."
        )

    else:

        st.subheader("Comparison of Methods")

        st.dataframe(
            comparison,
            use_container_width=True
        )

        # ----------------------------------------------------
        # METRICS
        # ----------------------------------------------------

        lp_row = comparison[
            comparison["method"]
            == "Transportation LP"
        ]

        integer_row = comparison[
            comparison["method"]
            == "Fixed-Charge Integer"
        ]

        greedy_row = comparison[
            comparison["method"]
            == "Greedy Baseline"
        ]

        if not lp_row.empty:

            lp_distance = float(
                lp_row.iloc[0][
                    "transportation_bike_km"
                ]
            )

            lp_improvement = float(
                lp_row.iloc[0][
                    "improvement_vs_greedy_%"
                ]
            )

        else:

            lp_distance = 0
            lp_improvement = 0

        if not integer_row.empty:

            integer_distance = float(
                integer_row.iloc[0][
                    "transportation_bike_km"
                ]
            )

            integer_improvement = float(
                integer_row.iloc[0][
                    "improvement_vs_greedy_%"
                ]
            )

            integer_routes = int(
                integer_row.iloc[0][
                    "routes_used"
                ]
            )

        else:

            integer_distance = 0
            integer_improvement = 0
            integer_routes = 0

        st.divider()

        st.subheader("Key Results")

        c1, c2, c3, c4 = st.columns(4)

        c1.metric(
            "LP Distance",
            f"{lp_distance:,.2f}"
        )

        c2.metric(
            "LP Improvement",
            f"{lp_improvement:.2f}%"
        )

        c3.metric(
            "Integer Improvement",
            f"{integer_improvement:.2f}%"
        )

        c4.metric(
            "Integer Routes",
            integer_routes
        )

        # ----------------------------------------------------
        # BAR CHART
        # ----------------------------------------------------

        st.subheader(
            "Transportation Distance Comparison"
        )

        chart_data = comparison[
            [
                "method",
                "transportation_bike_km"
            ]
        ].set_index("method")

        st.bar_chart(chart_data)

        # ----------------------------------------------------
        # IMPROVEMENT CHART
        # ----------------------------------------------------

        st.subheader(
            "Improvement Compared with Greedy Baseline"
        )

        improvement_data = comparison[
            [
                "method",
                "improvement_vs_greedy_%"
            ]
        ].set_index("method")

        st.bar_chart(improvement_data)

        # ----------------------------------------------------
        # INTERPRETATION
        # ----------------------------------------------------

        st.subheader("Interpretation")

        st.success(
            f"Transportation LP achieves the lowest "
            f"transportation distance: "
            f"{lp_distance:,.2f} bike-km, representing "
            f"a {lp_improvement:.2f}% improvement over "
            f"the Greedy Baseline."
        )

        st.info(
            f"Fixed-Charge Integer Programming uses "
            f"{integer_routes} routes and achieves "
            f"a {integer_improvement:.2f}% improvement "
            f"over the Greedy Baseline."
        )


# ============================================================
# VALIDATION
# ============================================================

elif page == "Validation":

    st.header("✅ Solution Validation")

    validation = load_csv(VALIDATION_FILE)

    if validation is None:

        st.warning(
            "Validation report not found. "
            "Run validate_results.py first."
        )

    else:

        st.markdown(
            """
            The optimization solutions are checked for:

            - Supply feasibility
            - Demand feasibility
            - Integer movement
            - Non-negative movement
            - Unmet demand
            - Bike-km calculation
            - Distance validity
            """
        )

        st.dataframe(
            validation,
            use_container_width=True
        )

        # ----------------------------------------------------
        # OVERALL STATUS
        # ----------------------------------------------------

        if "overall_validation" in validation.columns:

            all_pass = (
                validation[
                    "overall_validation"
                ].astype(str).str.upper() == "PASS"
            ).all()

            if all_pass:

                st.success(
                    "ALL OPTIMIZATION SOLUTIONS "
                    "PASSED VALIDATION."
                )

            else:

                st.error(
                    "One or more optimization "
                    "solutions require attention."
                )

        # ----------------------------------------------------
        # VALIDATION SUMMARY
        # ----------------------------------------------------

        st.subheader("Validation Summary")

        for _, row in validation.iterrows():

            method_name = row["method"]

            if str(
                row["overall_validation"]
            ).upper() == "PASS":

                st.success(
                    f"{method_name}: PASS"
                )

            else:

                st.error(
                    f"{method_name}: "
                    f"REQUIRES ATTENTION"
                )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "CitiBike Operations Research Project | "
    "Transportation LP + Fixed-Charge Integer Programming"
)