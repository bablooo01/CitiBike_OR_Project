# 🚲 Data-Driven Bike-Sharing Rebalancing Optimization

## Operations Research Project – 23MNG336

A data-driven Operations Research framework for optimizing bicycle redistribution between surplus and deficit CitiBike stations using Transportation Linear Programming and Fixed-Charge Integer Programming.

---

## 📌 Project Overview

Bike-sharing systems frequently experience an imbalance in bicycle availability across stations.

Some stations become empty during peak demand periods, preventing users from renting bicycles, while other stations become full, preventing users from returning bicycles.

This project develops an optimization-based framework to determine how bicycles should be redistributed between surplus and deficit stations while minimizing transportation effort.

The project uses CitiBike trip history data from June 2026 to identify station-level supply and demand during the evening peak period.

Three approaches are implemented:

1. Greedy Nearest-Neighbor Heuristic – baseline
2. Transportation Linear Programming – formal OR model
3. Fixed-Charge Integer Programming – formal OR model

The optimization results are compared based on transportation distance, active redistribution routes, number of bikes moved, and feasibility.

An interactive Streamlit dashboard is also provided for data loading, statistics, optimization selection, execution, and result comparison.

---

# 🎯 Aim

To develop a data-driven Operations Research framework for efficient redistribution of bicycles between surplus and deficit CitiBike stations by minimizing total transportation distance while satisfying station demand.

---

# ❗ Problem Statement

CitiBike stations experience spatial and temporal imbalance in bicycle availability.

Some stations have excess bicycles while others experience shortages. Manual or simple local redistribution strategies may result in unnecessary transportation distance and operational effort.

Therefore, this project addresses the following problem:

> Given a set of surplus and deficit CitiBike stations, determine an efficient redistribution plan that satisfies station demand while minimizing total bicycle transportation distance and, where applicable, reducing the number of active redistribution routes.

---

# 🎯 Objectives

The major objectives of the project are:

1. Analyze CitiBike trip data to understand station-level bicycle imbalance.

2. Identify surplus and deficit stations during the evening peak period.

3. Construct a distance-based transportation cost matrix between supply and demand stations.

4. Develop a Greedy Nearest-Neighbor heuristic as a baseline.

5. Formulate and solve a Transportation Linear Programming model.

6. Formulate and solve a Fixed-Charge Integer Programming model.

7. Compare the performance of the baseline and optimization approaches.

8. Validate all optimization solutions against supply, demand, integrality, and feasibility constraints.

9. Develop an interactive Streamlit dashboard for data loading, statistics, optimization execution, and result comparison.

---

# 📊 Dataset

## CitiBike Trip History – June 2026

The project uses publicly available CitiBike trip history data for June 2026.

The raw dataset contains trip-level information including:

- Start station ID
- Start station name
- Start station latitude
- Start station longitude
- End station ID
- End station name
- End station latitude
- End station longitude
- Trip start timestamp
- Trip end timestamp

The raw trip-level data is transformed into station-level supply and demand information required for the Operations Research models.

---

# 🔄 Data Processing Pipeline

The complete pipeline is:

```text
Raw CitiBike Trip Data
        ↓
Data Cleaning
        ↓
Station ID Normalization
        ↓
Evening Peak Filtering
        ↓
Station-Level Aggregation
        ↓
Surplus / Deficit Identification
        ↓
Optimization Station Selection
        ↓
Distance Calculation
        ↓
Transportation Cost Matrix
        ↓
Optimization Models
        ↓
Comparison
        ↓
Validation
        ↓
Streamlit Dashboard