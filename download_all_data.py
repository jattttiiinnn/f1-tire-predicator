# download_all_data.py
import fastf1
import os
import pandas as pd

def download_race_data(year: int, grand_prix: str, driver_code: str, output_path: str):
    """
    Download F1 race lap data for a specific Grand Prix and driver.
    Saves data to CSV file with lap number, lap time, tire compound, and tire age.
    """
    try:
        # Enable FastF1 caching
        fastf1.Cache.enable_cache('data/cache')

        # Load session (R = Race)
        print(f"\n🏁 Loading {grand_prix} {year} Race...")
        session = fastf1.get_session(year, grand_prix, 'R')
        session.load()

        # Filter laps for the specific driver
        driver_laps = session.laps.pick_driver(driver_code)

        if driver_laps.empty:
            raise ValueError(f"No lap data found for driver {driver_code} in {grand_prix}")

        # Create clean DataFrame
        df = pd.DataFrame({
            'lap_number': driver_laps['LapNumber'],
            'lap_time': driver_laps['LapTime'].dt.total_seconds(),
            'tire_compound': driver_laps['Compound'],
            'tire_age': driver_laps['TyreLife'],
        })

        # Drop invalid/missing values
        df = df.dropna(subset=['lap_time'])
        df = df[(df['lap_time'] > 50) & (df['lap_time'] < 200)]

        # Save to CSV
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        df.to_csv(output_path, index=False)

        print(f"✅ Saved {len(df)} laps for {driver_code} ({grand_prix} {year}) → {output_path}")
        print(df.head())

    except Exception as e:
        print(f"❌ Failed to download {grand_prix}: {e}")

def main():
    races = [
        ("Bahrain", "data/bahrain_2024_hamilton.csv"),
        ("Monaco", "data/monaco_2024_hamilton.csv"),
        ("Silverstone", "data/silverstone_2024_hamilton.csv"),
    ]

    for gp_name, file_path in races:
        download_race_data(2024, gp_name, "HAM", file_path)

if __name__ == "__main__":
    main()
