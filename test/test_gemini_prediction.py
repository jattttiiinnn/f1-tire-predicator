"""
Test script for Gemini tire degradation prediction.
"""

from modules.gemini_handler import create_prediction_prompt, get_prediction

# Example race context (from your create_ai_context example)
context = """=== F1 Tire Performance Context ===
Current Lap: 15
Tire Compound: Medium
Tire Age (laps): 15
Average Degradation Rate (last 10 laps): 0.348 s/lap
Track Temperature: 39.5 °C
Performance Pattern: degradation accelerating

Recent Lap Data:
Lap  6: time=93.100s, deg=0.000s
Lap  7: time=93.400s, deg=0.300s
Lap  8: time=93.700s, deg=0.300s
Lap  9: time=94.100s, deg=0.400s
Lap 10: time=94.500s, deg=0.400s
Lap 11: time=94.800s, deg=0.300s
Lap 12: time=95.100s, deg=0.300s
Lap 13: time=95.400s, deg=0.300s
Lap 14: time=95.900s, deg=0.500s
Lap 15: time=96.200s, deg=0.300s

Summary: Tire degradation appears to be degradation accelerating.
"""

if __name__ == "__main__":
    try:
        print("Building prediction prompt...")
        prompt = create_prediction_prompt(context, target_laps=10)

        print("\nSending prompt to Gemini...")
        response = get_prediction(prompt)

        print("\n=== GEMINI RESPONSE ===\n")
        print(response)

    except Exception as e:
        print(f"[FATAL ERROR] Test failed: {e}")
