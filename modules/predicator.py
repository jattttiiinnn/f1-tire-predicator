# """
# Predictor module — integrates data processing and Gemini AI
# to predict F1 tire degradation patterns and future lap times.
# """

# import traceback
# from modules.data_processor import (
#     load_race_data,
#     calculate_degradation,
#     create_ai_context,
# )
# from modules.gemini_handler import (
#     create_prediction_prompt,
#     get_prediction,
#     parse_prediction_response,
# )


# def predict_tire_degradation(csv_file, current_lap, target_laps=15):
#     """
#     Main function: predict tire degradation
    
#     Args:
#         csv_file: path to race data CSV
#         current_lap: int, current lap number
#         target_laps: int, how many laps to predict
        
#     Returns:
#         dict with predictions and metadata
#     """
#     result = {
#         "status": "failed",
#         "predictions": None,
#         "reasoning": None,
#         "error": None,
#     }

#     try:
#         # 1️⃣ Load race data
#         print(f"Loading race data from: {csv_file}")
#         df = load_race_data(csv_file)

#         # 2️⃣ Calculate degradation metrics
#         print("Calculating tire degradation metrics...")
#         df = calculate_degradation(df)

#         # 3️⃣ Create context for AI
#         print(f"Building AI context for lap {current_lap}...")
#         context = create_ai_context(df, current_lap)

#         # 4️⃣ Build prediction prompt
#         prompt = create_prediction_prompt(context, target_laps)

#         # 5️⃣ Send prompt to Gemini API
#         print("Querying Gemini for predictions...")
#         response_text = get_prediction(prompt)

#         # 6️⃣ Parse AI response into structured data
#         print("Parsing Gemini response...")
#         parsed = parse_prediction_response(response_text)

#         if not parsed:
#             raise ValueError("Unable to parse AI response into structured JSON.")

#         # 7️⃣ Return structured result
#         result.update({
#             "status": "success",
#             "predictions": parsed.get("predictions", []),
#             "reasoning": parsed.get("reasoning", ""),
#         })
#         return result

#     except Exception as e:
#         result["error"] = f"{type(e).__name__}: {e}"
#         traceback.print_exc()
#         return result

# def recommend_pit_stop(predictions, threshold=2.0):
#     """
#     Analyze predictions and recommend pit stop timing

#     Args:
#         predictions: list of dicts, each with keys at least:
#                      {"lap": int, "predicted_time": float, ...}
#                      Predictions should be ordered by lap ascending.
#         threshold: float, cumulative degradation threshold in seconds

#     Returns:
#         dict:
#         {
#           "recommended_lap": int | None,
#           "window": [start_lap, end_lap],
#           "reasoning": str,
#           "time_lost": float
#         }
#     """
#     # Validation
#     if not predictions or not isinstance(predictions, list):
#         return {
#             "recommended_lap": None,
#             "window": [None, None],
#             "reasoning": "No predictions provided.",
#             "time_lost": 0.0
#         }

#     # Ensure predictions sorted by lap
#     try:
#         predictions = sorted(predictions, key=lambda x: int(x["lap"]))
#     except Exception:
#         return {
#             "recommended_lap": None,
#             "window": [None, None],
#             "reasoning": "Invalid prediction format: could not sort by 'lap'.",
#             "time_lost": 0.0
#         }

#     # Baseline is first predicted lap time
#     try:
#         baseline_time = float(predictions[0]["predicted_time"])
#     except Exception:
#         return {
#             "recommended_lap": None,
#             "window": [None, None],
#             "reasoning": "Invalid prediction format: missing or non-numeric 'predicted_time'.",
#             "time_lost": 0.0
#         }

#     # Compute degradation per predicted lap relative to baseline, and cumulative
#     cumulative = 0.0
#     cumulative_list = []
#     for p in predictions:
#         lap_time = float(p["predicted_time"])
#         deg = lap_time - baseline_time  # seconds slower than baseline
#         # deg could be negative if model predicts faster laps; we keep actual cumulative (summing positive increases)
#         # But requirement says cumulative degradation — interpret as cumulative increase (summing max(0, deg) differences lap-to-lap).
#         cumulative_list.append(deg)

#     # For cumulative degradation over laps, use deg relative to baseline (monotonic increase expected)
#     # Find first lap where cumulative degradation > threshold
#     recommended = None
#     recommended_idx = None
#     time_lost = 0.0

#     for idx, deg in enumerate(cumulative_list):
#         # Use deg as cumulative from baseline; if deg is negative, treat as 0 for cumulative loss
#         cum_deg = max(0.0, deg)
#         if cum_deg > threshold:
#             recommended_idx = idx
#             recommended = int(predictions[idx]["lap"])
#             time_lost = cum_deg
#             break

#     # If not exceeded threshold within predictions, recommend last lap (decision: degrade to end)
#     if recommended is None:
#         recommended_idx = len(predictions) - 1
#         recommended = int(predictions[-1]["lap"])
#         time_lost = max(0.0, cumulative_list[-1])
#         reasoning = (
#             f"Threshold of {threshold:.2f}s not reached within prediction horizon. "
#             f"Recommend pitting by the last predicted lap ({recommended}) if no improvement expected."
#         )
#     else:
#         reasoning = (
#             f"Cumulative degradation exceeded {threshold:.2f}s at lap {recommended}. "
#             f"Estimated time lost if not pitting: {time_lost:.3f}s."
#         )

#     # Build 3-lap window (±1 lap), clamp to prediction range
#     lap_numbers = [int(p["lap"]) for p in predictions]
#     min_lap = min(lap_numbers)
#     max_lap = max(lap_numbers)
#     window_start = max(min_lap, recommended - 1)
#     window_end = min(max_lap, recommended + 1)

#     return {
#         "recommended_lap": recommended,
#         "window": [window_start, window_end],
#         "reasoning": reasoning,
#         "time_lost": float(round(time_lost, 3)),
#     }


# modules/predictor.py
import os
import random
import pandas as pd
import google.generativeai as genai
from modules.data_processor import load_race_data, calculate_degradation, create_ai_context
from modules.gemini_handler import create_prediction_prompt, get_prediction, parse_prediction_response

# Existing functions above ...
def predict_tire_degradation(track_name: str, current_lap: int = 10, target_laps: int = 15):
    """
    Predict tire degradation using Gemini API based on selected track.
    """
    TRACK_FILE_MAP = {
        "Bahrain GP 2024": "data/bahrain_2024_hamilton.csv",
        "Monaco GP 2024": "data/monaco_2024_hamilton.csv",
        "British GP 2024 (Silverstone)": "data/silverstone_2024_hamilton.csv",
    }

    csv_file = TRACK_FILE_MAP.get(track_name)
    if not csv_file or not os.path.exists(csv_file):
        return {"status": "error", "error": f"Data file not found for {track_name}"}

    try:
        df = pd.read_csv(csv_file)
        
        # Filter data UP TO current lap
        historical_data = df[df['lap_number'] <= current_lap].tail(10)
        
        # Get most recent lap time
        if len(historical_data) > 0:
            last_lap_time = historical_data.iloc[-1]['lap_time']
            last_lap_num = int(historical_data.iloc[-1]['lap_number'])
        else:
            return {"status": "error", "error": "Not enough historical data"}
        
        # Calculate total race laps
        total_laps = int(df['lap_number'].max())
        remaining_laps = total_laps - current_lap
        
        # Limit predictions to remaining laps
        target_laps = min(target_laps, remaining_laps)
        
    except Exception as e:
        return {"status": "error", "error": f"Failed to load data: {e}"}

    # --- Build Improved Prompt ---
    prompt = f"""
You are an F1 race strategist analyzing {track_name} for Lewis Hamilton.

RACE CONTEXT:
- Current lap: {current_lap}
- Total race laps: {total_laps}
- Remaining laps: {remaining_laps}
- Predict next: {target_laps} laps

RECENT LAP TIMES (last 10 laps):
{historical_data[['lap_number', 'lap_time', 'tire_compound', 'tire_age']].to_string(index=False)}

TASK:
Predict lap times for laps {current_lap + 1} through {current_lap + target_laps}.
Consider tire degradation patterns shown in the data.

IMPORTANT RULES:
- Lap numbers must be sequential starting from {current_lap + 1}
- Do NOT exceed lap {total_laps}
- Lap times should increase gradually (degradation)
- Base predictions on the pattern shown in recent laps

Return ONLY valid JSON with this exact structure:
{{
    "predictions": [
        {{"lap": {current_lap + 1}, "predicted_time": 95.5, "confidence": 0.85}},
        {{"lap": {current_lap + 2}, "predicted_time": 95.7, "confidence": 0.83}},
        ...
    ],
    "reasoning": "Your explanation of degradation pattern and pit strategy recommendation here"
}}
"""

    try:
        model = genai.GenerativeModel("gemini-2.0-flash-exp")
        response = model.generate_content(prompt)
        text = response.text.strip()

        # --- Parse JSON safely ---
        import json
        import re
        
        # Remove markdown code blocks if present
        text = re.sub(r'```json\s*', '', text)
        text = re.sub(r'```\s*', '', text)
        
        # Find JSON object
        start = text.find("{")
        end = text.rfind("}") + 1
        
        if start == -1 or end == 0:
            return {"status": "error", "error": "No valid JSON found in response"}
        
        json_str = text[start:end]
        parsed = json.loads(json_str)

        # Validate predictions
        predictions = parsed.get("predictions", [])
        
        # Filter out invalid laps (beyond race end)
        valid_predictions = [
            p for p in predictions 
            if p.get("lap", 999) <= total_laps
        ]
        
        if not valid_predictions:
            return {"status": "error", "error": "No valid predictions generated"}

        return {
            "status": "success",
            "predictions": valid_predictions,
            "reasoning": parsed.get("reasoning", "No reasoning provided"),
        }

    except json.JSONDecodeError as e:
        return {"status": "error", "error": f"Failed to parse JSON: {e}"}
    except Exception as e:
        return {"status": "error", "error": f"Gemini API call failed: {e}"}

def recommend_pit_stop(predictions, threshold=2.0):
    """Simple pit stop recommendation logic."""
    if not predictions:
        return {"recommended_lap": None, "reasoning": "No prediction data", "window": (0, 0), "time_lost": 0.0}

    times = [p["predicted_time"] for p in predictions]
    diffs = [t - times[0] for t in times]
    for i, d in enumerate(diffs):
        if d >= threshold:
            return {
                "recommended_lap": predictions[i]["lap"],
                "reasoning": f"Lap time degraded by {d:.2f}s compared to baseline.",
                "window": (predictions[max(0, i-1)]["lap"], predictions[min(i+1, len(predictions)-1)]["lap"]),
                "time_lost": d,
            }

    return {
        "recommended_lap": predictions[-1]["lap"],
        "reasoning": "Tire degradation within safe limits; extend current stint.",
        "window": (predictions[-2]["lap"], predictions[-1]["lap"]),
        "time_lost": 0.0,
    }


def compare_strategies(csv_file, current_lap):
    """
    Compare 1-stop vs 2-stop strategies using AI predictions or simplified models.
    
    Args:
        csv_file (str): Path to the race data CSV.
        current_lap (int): Current lap number.
    
    Returns:
        dict with:
        {
            "strategies": [
                {"name": "1-Stop Strategy", "pit_laps": [25], "finish_time": 5500.0,
                 "pros": "...", "cons": "..."},
                {"name": "2-Stop Strategy", "pit_laps": [20, 40], "finish_time": 5400.0,
                 "pros": "...", "cons": "..."}
            ],
            "recommended": "2-Stop Strategy"
        }
    """
    try:
        # Load and process data
        df = load_race_data(csv_file)
        df = calculate_degradation(df)

        # Simple heuristic simulation
        total_laps = int(df["lap_number"].max() or 57)
        remaining_laps = total_laps - current_lap

        # Simulated degradation per lap (average from data)
        avg_deg = df["degradation"].mean(skipna=True)
        if pd.isna(avg_deg):
            avg_deg = 0.12  # fallback if missing data

        # Base lap time (most recent)
        base_time = df[df["lap_number"] == current_lap]["lap_time"].values
        base_time = base_time[0] if len(base_time) > 0 else 90.0

        # --- Strategy 1: One-stop (around lap 25)
        pit_1_laps = [25]
        pit_loss_1 = 22.0  # avg pit loss in seconds
        finish_time_1 = base_time * remaining_laps + pit_loss_1 + (avg_deg * remaining_laps * 1.05)

        # --- Strategy 2: Two-stop (around lap 20 + 40)
        pit_2_laps = [20, 40]
        pit_loss_2 = 22.0 * 2
        finish_time_2 = base_time * remaining_laps + pit_loss_2 + (avg_deg * remaining_laps * 0.85)

        # Construct strategy info
        strategies = [
            {
                "name": "1-Stop Strategy",
                "pit_laps": pit_1_laps,
                "finish_time": round(finish_time_1, 2),
                "pros": "Simpler, less risk of pit errors.",
                "cons": "Higher tire wear; may lose pace in final laps.",
            },
            {
                "name": "2-Stop Strategy",
                "pit_laps": pit_2_laps,
                "finish_time": round(finish_time_2, 2),
                "pros": "Fresher tires; more consistent performance.",
                "cons": "Extra pit stop adds risk and time.",
            },
        ]

        # Choose recommended strategy (lowest predicted finish time)
        recommended = min(strategies, key=lambda x: x["finish_time"])["name"]

        return {
            "status": "success",
            "strategies": strategies,
            "recommended": recommended,
        }

    except Exception as e:
        return {"status": "error", "error": str(e)}
