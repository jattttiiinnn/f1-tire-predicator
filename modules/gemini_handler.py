def create_prediction_prompt(context, target_laps=15):
    """
    Build prompt for Gemini to predict tire degradation and lap times.
    
    Args:
        context (str): Formatted race data context from data_processor.create_ai_context()
        target_laps (int): Number of future laps to predict
        
    Returns:
        str: Complete prompt text for Gemini AI
    """

    # ---------------------------------------------------------------------
    # 1. Define role and purpose
    # ---------------------------------------------------------------------
    role_description = (
        "You are an expert F1 race strategist and data analyst. "
        "Your job is to analyze lap times, tire wear, and degradation patterns "
        "to forecast future lap times for the same tire stint."
    )

    # ---------------------------------------------------------------------
    # 2. Build structured, detailed instructions
    # ---------------------------------------------------------------------
    instructions = (
        "Analyze the provided race telemetry and tire degradation context. "
        "Focus on how lap times are increasing (slowing) over time, "
        "and infer the degradation rate trend. Use that trend to estimate "
        f"the next {target_laps} lap times. Consider tire compound, age, and track temperature "
        "when making predictions. Include a reasoning summary describing how you derived the results."
    )

    # ---------------------------------------------------------------------
    # 3. Specify the required output format
    # ---------------------------------------------------------------------
    output_format = (
        "Return your answer in **strict JSON format** like this:\n"
        "{\n"
        "  \"predictions\": [\n"
        "    {\"lap\": 16, \"predicted_time\": 75.234, \"confidence\": 0.85},\n"
        "    {\"lap\": 17, \"predicted_time\": 75.411, \"confidence\": 0.83},\n"
        "    ...\n"
        "  ],\n"
        "  \"reasoning\": \"Explain the trend, degradation pattern, and key insights.\"\n"
        "}\n\n"
        "Ensure floating-point lap times are in seconds with 3 decimal precision. "
        "Confidence should be a value between 0.0 and 1.0 representing prediction certainty."
    )

    # ---------------------------------------------------------------------
    # 4. Combine everything into a single Gemini-ready prompt
    # ---------------------------------------------------------------------
    prompt = (
        f"{role_description}\n\n"
        f"{instructions}\n\n"
        "=== CONTEXT DATA START ===\n"
        f"{context}\n"
        "=== CONTEXT DATA END ===\n\n"
        f"{output_format}\n"
        "Emphasize the degradation pattern (accelerating, stable, or recovering) in your reasoning."
    )

    return prompt

import time
import google.generativeai as genai
from config import API_KEY


def get_prediction(prompt):
    """
    Send prompt to Gemini and get response
    
    Args:
        prompt (str): The prediction prompt
        
    Returns:
        str: AI response text or error message
    """
    # ---------------------------------------------------------------------
    # 1. Check for API key
    # ---------------------------------------------------------------------
    if not API_KEY:
        return "[ERROR] Missing Gemini API key. Please set it in your .env file as GEMINI_API_KEY=your_key_here."

    # ---------------------------------------------------------------------
    # 2. Initialize Gemini model
    # ---------------------------------------------------------------------
    try:
        genai.configure(api_key=API_KEY)
        model = genai.GenerativeModel("gemini-2.5-flash")
    except Exception as e:
        return f"[ERROR] Failed to initialize Gemini model: {e}"

    # ---------------------------------------------------------------------
    # 3. Attempt generation with retry logic
    # ---------------------------------------------------------------------
    max_retries = 3
    for attempt in range(1, max_retries + 1):
        try:
            response = model.generate_content(prompt)
            if not response or not response.text:
                raise ValueError("Empty or invalid response from Gemini.")
            return response.text.strip()

        except Exception as e:
            err_msg = str(e).lower()

            # Network or quota related
            if "rate limit" in err_msg or "quota" in err_msg:
                print(f"[WARN] Rate limit reached (attempt {attempt}/{max_retries}). Retrying in 2s...")
                time.sleep(2)
            elif "network" in err_msg or "timeout" in err_msg:
                print(f"[WARN] Network issue (attempt {attempt}/{max_retries}). Retrying in 2s...")
                time.sleep(2)
            else:
                print(f"[ERROR] Unexpected error (attempt {attempt}/{max_retries}): {e}")
                break

    # ---------------------------------------------------------------------
    # 4. If all retries failed
    # ---------------------------------------------------------------------
    return "[ERROR] Failed to get response from Gemini after multiple attempts."

import json
import re


def parse_prediction_response(response_text):
    """
    Extract structured data from Gemini response
    
    Args:
        response_text (str): Raw AI response
        
    Returns:
        dict | None: Parsed data with structure:
        {
          "predictions": [ {"lap": int, "predicted_time": float, "confidence": float}, ... ],
          "reasoning": str
        }
        Returns None if parsing fails.
    """

    if not response_text or not isinstance(response_text, str):
        print("[ERROR] Invalid response_text: empty or non-string")
        return None

    data = None

    # ---------------------------------------------------------------------
    # 1. Try parsing as pure JSON directly
    # ---------------------------------------------------------------------
    try:
        data = json.loads(response_text)
        if isinstance(data, dict):
            return _validate_prediction_json(data)
    except Exception:
        pass

    # ---------------------------------------------------------------------
    # 2. Extract JSON from Markdown code block ```json ... ```
    # ---------------------------------------------------------------------
    try:
        match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", response_text, re.DOTALL | re.IGNORECASE)
        if match:
            json_text = match.group(1)
            data = json.loads(json_text)
            return _validate_prediction_json(data)
    except Exception:
        pass

    # ---------------------------------------------------------------------
    # 3. Fallback: extract JSON-like content using regex (first {...})
    # ---------------------------------------------------------------------
    try:
        match = re.search(r"(\{[\s\S]*\})", response_text)
        if match:
            json_text = match.group(1)
            data = json.loads(json_text)
            return _validate_prediction_json(data)
    except Exception:
        pass

    # ---------------------------------------------------------------------
    # 4. Complete failure
    # ---------------------------------------------------------------------
    print("[ERROR] Failed to parse Gemini response as JSON.")
    return None


def _validate_prediction_json(data):
    """
    Internal: validate and normalize the parsed JSON.
    """
    if not isinstance(data, dict):
        print("[ERROR] Parsed data is not a dict.")
        return None

    predictions = data.get("predictions")
    reasoning = data.get("reasoning")

    if not predictions or not isinstance(predictions, list):
        print("[ERROR] Missing or invalid 'predictions' list.")
        return None

    if not reasoning or not isinstance(reasoning, str):
        reasoning = "No reasoning provided."

    cleaned_predictions = []
    for p in predictions:
        try:
            cleaned_predictions.append({
                "lap": int(p.get("lap")),
                "predicted_time": float(p.get("predicted_time")),
                "confidence": float(p.get("confidence")),
            })
        except Exception:
            continue

    if not cleaned_predictions:
        print("[ERROR] No valid prediction entries found.")
        return None

    return {"predictions": cleaned_predictions, "reasoning": reasoning}
