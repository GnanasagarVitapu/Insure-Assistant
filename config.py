from dotenv import load_dotenv
import os
from openai import OpenAI

load_dotenv()

# Load environment variables from .env file
base_url = os.getenv("API_BASE_URL")
api_key = os.getenv("API_KEY")
model_name = os.getenv("MODEL_NAME")
embedding_model = os.getenv("EMBEDDING_MODEL")
emb_api_key = os.getenv("OA_API_KEY")
emb_api_base_url = os.getenv("OA_API_BASE_URL")

#creating openai client
client = OpenAI(base_url=base_url, api_key=api_key)
emb_client = OpenAI(base_url=emb_api_base_url, api_key=emb_api_key)