"""
Test parser for Gemini JSON responses in various formats.
"""

from modules.gemini_handler import parse_prediction_response

def run_tests():
    # ---------------------------------------------------------------------
    # 1️⃣ Pure JSON response (clean structure)
    # ---------------------------------------------------------------------
    response_json = """
    {
      "predictions": [
        {"lap": 16, "predicted_time": 96.45, "confidence": 0.88},
        {"lap": 17, "predicted_time": 96.68, "confidence": 0.86}
      ],
      "reasoning": "Stable degradation with moderate wear."
    }
    """

    # ---------------------------------------------------------------------
    # 2️⃣ JSON inside Markdown code block
    # ---------------------------------------------------------------------
    response_markdown = """
    Here are your results:

    ```json
    {
      "predictions": [
        {"lap": 16, "predicted_time": 96.55, "confidence": 0.87},
        {"lap": 17, "predicted_time": 96.80, "confidence": 0.85}
      ],
      "reasoning": "Slight degradation increase over laps."
    }
    ```
    """

    # ---------------------------------------------------------------------
    # 3️⃣ JSON mixed with explanatory text
    # ---------------------------------------------------------------------
    response_mixed = """
    The model predicts as follows. See structured JSON below:

    {
      "predictions": [
        {"lap": 16, "predicted_time": 96.70, "confidence": 0.84},
        {"lap": 17, "predicted_time": 96.95, "confidence": 0.82}
      ],
      "reasoning": "Tire wear accelerating slightly, confidence moderate."
    }

    End of report.
    """

    # ---------------------------------------------------------------------
    # Run tests for all 3 response formats
    # ---------------------------------------------------------------------
    test_cases = [
        ("Pure JSON", response_json),
        ("Markdown JSON Block", response_markdown),
        ("Mixed Text + JSON", response_mixed),
    ]

    for name, sample in test_cases:
        print(f"\n=== TEST CASE: {name} ===")
        result = parse_prediction_response(sample)
        if result:
            print("Parsed Output:")
            print(result)
        else:
            print("❌ Failed to parse response.")


if __name__ == "__main__":
    run_tests()
