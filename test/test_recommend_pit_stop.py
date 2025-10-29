"""
Test recommend_pit_stop() with sample predictions and different thresholds.
"""

from modules.predicator import recommend_pit_stop

# Sample predictions produced by AI (ordered)
sample_predictions = [
    {"lap": 16, "predicted_time": 95.672, "confidence": 0.87},
    {"lap": 17, "predicted_time": 95.941, "confidence": 0.85},
    {"lap": 18, "predicted_time": 96.320, "confidence": 0.84},
    {"lap": 19, "predicted_time": 96.700, "confidence": 0.82},
    {"lap": 20, "predicted_time": 97.150, "confidence": 0.80},
    {"lap": 21, "predicted_time": 97.600, "confidence": 0.78},
    {"lap": 22, "predicted_time": 98.100, "confidence": 0.75},
    {"lap": 23, "predicted_time": 98.650, "confidence": 0.72},
    {"lap": 24, "predicted_time": 99.200, "confidence": 0.70},
    {"lap": 25, "predicted_time": 99.800, "confidence": 0.68},
]

thresholds = [1.5, 2.0, 2.5]

for th in thresholds:
    result = recommend_pit_stop(sample_predictions, threshold=th)
    print("\n--- Threshold:", th, "seconds ---")
    print("Recommended lap:", result["recommended_lap"])
    print("Pit window:", result["window"])
    print("Estimated time lost if no pit:", result["time_lost"], "s")
    print("Reasoning:", result["reasoning"])
