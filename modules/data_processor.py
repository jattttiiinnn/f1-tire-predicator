import pandas as pd

def load_race_data(csv_file):
    """
    Load F1 race data from CSV and clean it

    Args:
        csv_file (str): Path to the CSV file

    Returns:
        pandas.DataFrame: Cleaned DataFrame with valid lap data
    """
    try:
        # 1. Load CSV file using pandas
        df = pd.read_csv(csv_file)

        # 2. Remove rows with missing lap times
        df = df.dropna(subset=["LapTime_seconds"])

        # 3. Convert lap time to float
        df["LapTime_seconds"] = df["LapTime_seconds"].astype(float)

        # 4. Ensure tire age is integer
        if "TyreLife" in df.columns:
            df["TyreLife"] = df["TyreLife"].fillna(0).astype(int)
        elif "tire_age" in df.columns:
            df["tire_age"] = df["tire_age"].fillna(0).astype(int)

        # 5. Remove invalid lap times (< 60s or > 150s)
        df = df[(df["LapTime_seconds"] >= 60) & (df["LapTime_seconds"] <= 150)]

        df = df.reset_index(drop=True)
        return df

    except FileNotFoundError:
        print(f"❌ Error: File not found — {csv_file}")
        return pd.DataFrame()
    except pd.errors.EmptyDataError:
        print(f"❌ Error: File is empty — {csv_file}")
        return pd.DataFrame()
    except Exception as e:
        print(f"❌ Unexpected error while loading {csv_file}: {e}")
        return pd.DataFrame()


# -------------------------------------------------------------------------
# NEW FUNCTION
# -------------------------------------------------------------------------
def calculate_degradation(df):
    """
    Calculate tire degradation metrics
    
    Args:
        df (DataFrame): Must contain 'LapTime_seconds' column
        
    Returns:
        DataFrame with added columns:
        - degradation: seconds slower than previous lap
        - cumulative_degradation: total time lost over laps
        - degradation_rate: rolling average degradation over 5 laps
    """
    if df.empty:
        print("⚠️ Empty DataFrame passed to calculate_degradation().")
        return df

    if "LapTime_seconds" not in df.columns:
        print("❌ Required column 'LapTime_seconds' not found in DataFrame.")
        return df

    df = df.copy()  # Avoid mutating original

    # 1. Calculate lap-to-lap degradation (difference from previous lap)
    df["degradation"] = df["LapTime_seconds"].diff()

    # 2. Handle first lap (no previous lap)
    df.loc[df["LapNumber"] == df["LapNumber"].min(), "degradation"] = 0.0

    # 3. Calculate cumulative degradation (sum of degradation over laps)
    df["cumulative_degradation"] = df["degradation"].cumsum()

    # 4. Calculate rolling average degradation (5-lap window)
    df["degradation_rate"] = df["degradation"].rolling(window=5, min_periods=1).mean()

    # 5. Ensure numeric consistency
    df[["degradation", "cumulative_degradation", "degradation_rate"]] = (
        df[["degradation", "cumulative_degradation", "degradation_rate"]].astype(float)
    )

    return df

def create_ai_context(df, current_lap):
    """
    Format race data into text context for Gemini AI
    
    Args:
        df (pandas.DataFrame): DataFrame with lap and degradation data
        current_lap (int): Current lap number
        
    Returns:
        str: Formatted text context describing tire performance trends
    """
    if df.empty:
        return "No race data available."

    if current_lap not in df["LapNumber"].values:
        return f"Lap {current_lap} not found in dataset."

    # ---------------------------------------------------------------------
    # 1. Extract the last 10 laps up to the current lap
    # ---------------------------------------------------------------------
    last_laps = df[df["LapNumber"] <= current_lap].tail(10)

    # ---------------------------------------------------------------------
    # 2. Gather general info
    # ---------------------------------------------------------------------
    latest = last_laps.iloc[-1]
    tire_compound = latest.get("Compound", "Unknown")
    tire_age = int(latest.get("TyreLife", 0))
    avg_degradation = round(last_laps["degradation_rate"].mean(), 3) if "degradation_rate" in last_laps else None
    track_temp = latest.get("TrackTemp", None) if "TrackTemp" in df.columns else None

    # ---------------------------------------------------------------------
    # 3. Analyze pattern (acceleration/deceleration of degradation)
    # ---------------------------------------------------------------------
    pattern = "stable"
    if "degradation_rate" in last_laps:
        rates = last_laps["degradation_rate"].dropna().values
        if len(rates) >= 3:
            if rates[-1] > rates[-3] * 1.2:
                pattern = "degradation accelerating"
            elif rates[-1] < rates[-3] * 0.8:
                pattern = "degradation slowing down"

    # ---------------------------------------------------------------------
    # 4. Format the recent laps into readable text
    # ---------------------------------------------------------------------
    lap_lines = []
    for _, row in last_laps.iterrows():
        lap_lines.append(
            f"Lap {int(row['LapNumber']):>2}: "
            f"time={row['LapTime_seconds']:.3f}s, "
            f"deg={row['degradation']:.3f}s"
        )
    laps_text = "\n".join(lap_lines)

    # ---------------------------------------------------------------------
    # 5. Build final AI-readable structured context
    # ---------------------------------------------------------------------
    context = [
        "=== F1 Tire Performance Context ===",
        f"Current Lap: {current_lap}",
        f"Tire Compound: {tire_compound}",
        f"Tire Age (laps): {tire_age}",
        f"Average Degradation Rate (last 10 laps): {avg_degradation} s/lap",
    ]

    if track_temp is not None and not pd.isna(track_temp):
        context.append(f"Track Temperature: {track_temp} °C")

    context.append(f"Performance Pattern: {pattern}")
    context.append("\nRecent Lap Data:")
    context.append(laps_text)
    context.append("\nSummary: Tire degradation appears to be " + pattern + ".")

    return "\n".join(context)
