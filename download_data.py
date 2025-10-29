#!/usr/bin/env python3
"""
download_data.py

Downloads Formula 1 race telemetry using the FastF1 library.

Steps:
1. Enables data caching to data/cache/
2. Downloads the Bahrain GP 2024 Race session
3. Extracts lap data for driver "HAM" (Lewis Hamilton)
4. Creates a DataFrame with:
   - Lap Number
   - Lap Time (in seconds)
   - Tire Compound
   - Tire Age (laps on current set)
5. Saves results to data/bahrain_2024_hamilton.csv
6. Prints summary: number of laps, first 5 rows, and statistics
"""

import os
import sys
import pandas as pd
import fastf1

def main():
    try:
        # ---------------------------------------------------------------------
        # 1. Enable FastF1 caching
        # ---------------------------------------------------------------------
        cache_dir = "data/cache"
        os.makedirs(cache_dir, exist_ok=True)
        fastf1.Cache.enable_cache(cache_dir)
        print(f"✅ FastF1 cache enabled at: {cache_dir}")

        # ---------------------------------------------------------------------
        # 2. Load Bahrain GP 2024 Race session
        # ---------------------------------------------------------------------
        print("⏳ Loading Bahrain GP 2024 Race session...")
        session = fastf1.get_session(2024, "Bahrain", "R")
        session.load()
        print("✅ Session loaded successfully!")

        # ---------------------------------------------------------------------
        # 3. Extract laps for driver 'HAM' (Lewis Hamilton)
        # ---------------------------------------------------------------------
        driver_code = "HAM"
        laps = session.laps.pick_driver(driver_code)

        if laps.empty:
            print(f"⚠️ No laps found for driver {driver_code}. Check driver code or session data.")
            sys.exit(1)

        # ---------------------------------------------------------------------
        # 4. Extract desired columns and clean data
        # ---------------------------------------------------------------------
        # Convert LapTime (timedelta) → seconds
        df = pd.DataFrame({
            "LapNumber": laps["LapNumber"],
            "LapTime_seconds": laps["LapTime"].dt.total_seconds(),
            "Compound": laps["Compound"],
            "TyreLife": laps["TyreLife"]
        })

        # Drop laps with missing or invalid lap times
        df = df.dropna(subset=["LapTime_seconds"])
        df = df[df["LapTime_seconds"] > 0]

        # ---------------------------------------------------------------------
        # 5. Save results to CSV
        # ---------------------------------------------------------------------
        output_path = "data/bahrain_2024_hamilton.csv"
        df.to_csv(output_path, index=False)
        print(f"💾 Data saved to: {output_path}")

        # ---------------------------------------------------------------------
        # 6. Print summary information
        # ---------------------------------------------------------------------
        print(f"\n📊 Total laps downloaded: {len(df)}\n")

        print("🔹 First 5 rows of data:")
        print(df.head().to_string(index=False))

        print("\n📈 Summary statistics:")
        print(df.describe(include="all"))

    except Exception as e:
        # ---------------------------------------------------------------------
        # Handle all unexpected errors gracefully
        # ---------------------------------------------------------------------
        print("\n❌ An error occurred while downloading or processing data.")
        print("Error type:", type(e).__name__)
        print("Error message:", str(e))
        print("\nPossible causes:")
        print("- No internet connection (FastF1 needs to download data).")
        print("- FastF1 or pandas not installed (run: pip install fastf1 pandas).")
        print("- API data unavailable or driver code typo.")
        sys.exit(1)


if __name__ == "__main__":
    main()
