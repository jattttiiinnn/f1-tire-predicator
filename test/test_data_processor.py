#!/usr/bin/env python3
"""
test_data_processor.py

Tests:
1. Loads race data CSV
2. Cleans it using load_race_data()
3. Calculates degradation metrics using calculate_degradation()
4. Prints stats, top degrading laps, and optional plot
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
from modules.data_processor import load_race_data, calculate_degradation


def main():
    # -----------------------------------------------------------------
    # 1. Load cleaned race data
    # -----------------------------------------------------------------
    csv_path = os.path.join("data", "bahrain_2024_hamilton.csv")
    print(f"📂 Loading race data from: {csv_path}")
    df = load_race_data(csv_path)

    if df.empty:
        print("⚠️ No data loaded — check CSV file path.")
        return

    # -----------------------------------------------------------------
    # 2. Calculate degradation metrics
    # -----------------------------------------------------------------
    df = calculate_degradation(df)

    print("\n✅ Data loaded and degradation metrics calculated!")
    print(f"Total laps: {len(df)}\n")

    # -----------------------------------------------------------------
    # 3. Show info and head
    # -----------------------------------------------------------------
    print("🔹 DataFrame info:")
    print(df.info())

    print("\n🔹 First 10 rows:")
    print(df.head(10).to_string(index=False))

    # -----------------------------------------------------------------
    # 4. Summary degradation statistics
    # -----------------------------------------------------------------
    print("\n📈 Degradation statistics:")
    print(df[["degradation", "cumulative_degradation", "degradation_rate"]].describe())

    # -----------------------------------------------------------------
    # 5. Find laps with highest degradation
    # -----------------------------------------------------------------
    high_deg = df.sort_values(by="degradation", ascending=False).head(5)
    print("\n🔥 Laps with highest degradation:")
    print(high_deg[["LapNumber", "LapTime_seconds", "degradation"]].to_string(index=False))

    # -----------------------------------------------------------------
    # 6. Optional visualization
    # -----------------------------------------------------------------
    try:
        plt.figure(figsize=(10, 6))
        plt.plot(df["LapNumber"], df["degradation_rate"], label="Degradation Rate (Rolling Avg)", linewidth=2)
        plt.plot(df["LapNumber"], df["degradation"], alpha=0.4, label="Lap-to-Lap Degradation", linestyle="--")
        plt.xlabel("Lap Number")
        plt.ylabel("Degradation (seconds)")
        plt.title("F1 Tire Degradation Trend — Hamilton, Bahrain 2024")
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.show()
    except Exception as e:
        print(f"⚠️ Could not generate plot: {e}")


if __name__ == "__main__":
    main()
