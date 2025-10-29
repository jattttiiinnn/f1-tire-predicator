"""
Configuration loader for environment variables.
Loads Gemini API key from .env file.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Read API key safely
API_KEY = os.getenv("GEMINI_API_KEY")

# Optional: helper check
if not API_KEY:
    print("[WARN] GEMINI_API_KEY not found in environment. Please set it in your .env file.")
