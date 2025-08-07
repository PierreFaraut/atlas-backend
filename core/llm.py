from pydantic_ai.models.google import GoogleModel, GoogleModelSettings
import os
from dotenv import load_dotenv

load_dotenv()

MODEL_NAME = os.environ.get("MODEL_NAME")
API_KEY = os.environ.get("GEMINI_API_KEY")

# provider = GoogleProvider(api_key=API_KEY)
settings = GoogleModelSettings(google_thinking_config={"include_thoughts": True})
model = GoogleModel(MODEL_NAME)
