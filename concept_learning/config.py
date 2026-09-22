from dotenv import load_dotenv
import os
from openai import OpenAI

load_dotenv()

# Load environment variables from .env file
embedding_model = os.getenv("EMBEDDING_MODEL")
emb_api_key = os.getenv("OA_API_KEY")
emb_api_base_url = os.getenv("OA_API_BASE_URL")

#creating openai client
emb_client = OpenAI(base_url=emb_api_base_url, api_key=emb_api_key)