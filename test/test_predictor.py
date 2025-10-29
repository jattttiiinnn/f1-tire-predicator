"""
Test script for modules/predictor.py
Runs a full prediction pipeline using sample race data.
"""

from modules.predicator import predict_tire_degradation

def run_prediction_test():
    # Path to your processed race data
    csv_file = "data/bahrain_2024_hamilton.csv"

    # Current lap number for which you want prediction
    current_lap = 15

    print("\n=== Running Tire Degradation Prediction ===")
    result = predict_tire_degradation(csv_file, current_lap=current_lap, target_laps=15)

    if result["status"] == "success":
        print("\n✅ Prediction successful!\n")

        print("=== Predicted Lap Times ===")
        for p in result["predictions"]:
            lap = p.get("lap")
            time = p.get("predicted_time")
            conf = p.get("confidence")
            print(f"Lap {lap}: {time:.3f} sec (Confidence: {conf:.2f})")

        print("\n=== AI Reasoning ===")
        print(result["reasoning"])

    else:
        print("\n❌ Prediction failed.")
        print(f"Error: {result['error']}")


if __name__ == "__main__":
    run_prediction_test()
