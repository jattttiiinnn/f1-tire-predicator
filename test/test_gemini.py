#!/usr/bin/env python3
"""
test_gemini.py

Simple test script to confirm Google Gemini integration using
the `google-generativeai` Python package.

What it does:
1. Loads GEMINI_API_KEY from a .env file
2. Configures the google.generativeai client
3. Initializes a Gemini Pro model (identifier used: "gemini-2.5-flash")
4. Sends a short test prompt and prints the result
5. Handles missing API key and runtime errors with clear messages
"""

import os
import sys

# Load environment variables from .env
try:
    from dotenv import load_dotenv
except Exception as e:
    print("Error: python-dotenv is not installed. Run: pip install python-dotenv")
    raise e

# Import the google generative AI library
try:
    import google.generativeai as genai
except Exception as e:
    print("Error: google-generativeai package not installed. Run: pip install google-generativeai")
    raise e

# Load .env into environment
load_dotenv()

def main():
    # 1) Get API key from environment variable
    api_key = os.getenv("GEMINI_API_KEY")

    # 2) Handle missing API key case
    if not api_key:
        print("ERROR: GEMINI_API_KEY not found in environment.")
        print("Please create a .env file with a line like:\n    GEMINI_API_KEY=your_google_gemini_api_key_here")
        sys.exit(1)

    # 3) Configure the google.generativeai client with your key
    try:
        genai.configure(api_key=api_key)
    except Exception as e:
        print("ERROR: Failed to configure google.generativeai with the provided API key.")
        print("Exception message:", str(e))
        sys.exit(1)

    # 4) Prepare the prompt
    prompt = "Explain F1 tire degradation in 2 sentences"

    # 5) Call the model - initialize the Gemini Pro model and generate response
    # NOTE: the exact model identifier may vary depending on your account / SDK version.
    # If "gemini-2.5-flash" does not exist for you, replace it with the correct model name.
    model_name = "gemini-2.5-flash"

    try:
        # Some SDK versions provide a GenerativeModel interface (model.generate_content)
        # If your version uses another API surface, adapt accordingly.
        model = genai.GenerativeModel(model_name)

        # Generate content from the model
        # Using .generate_content() as a commonly used method in some SDK releases.
        response = model.generate_content(prompt)

        # response may have different structure depending on SDK version;
        # attempt to print the most common attributes.
        if hasattr(response, "text"):
            # Many SDKs expose the text as response.text
            print("\n--- Gemini response (text) ---\n")
            print(response.text)
        else:
            # Otherwise, print the whole response object for debugging
            print("\n--- Gemini response (raw) ---\n")
            print(response)

    except Exception as e:
        print("ERROR: A problem occurred while calling the Gemini model.")
        print("Exception type:", type(e).__name__)
        print("Exception message:", str(e))
        print("\nTips:")
        print("- Verify your GEMINI_API_KEY is valid and active.")
        print("- Ensure the model identifier (currently set to '{}') is correct for your account.".format(model_name))
        print("- If the SDK changed, check the google-generativeai docs for the current call pattern.")
        sys.exit(1)


if __name__ == "__main__":
    main()
