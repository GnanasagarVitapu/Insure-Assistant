from dotenv import load_dotenv
import os
from openai import OpenAI

load_dotenv()

# Load environment variables from .env file
base_url = os.getenv("OPENROUTER_API_BASE_URL")
api_key = os.getenv("OPENROUTER_API_KEY")
model_name = os.getenv("MODEL_NAME")

#creating openai client
client = OpenAI(base_url=base_url, api_key=api_key)