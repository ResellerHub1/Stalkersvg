import os
from dotenv import load_dotenv

# Load .env file from project root
env_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path=env_path)

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
KEEPA_API_KEY = os.getenv("KEEPA_API_KEY")
MONGO_URI = os.getenv("MONGO_URI")

TIER_LIMITS = {
    "Free": 0,
    "Silver": 3,
    "Gold": 5,
    "Admin": float('inf')
}
print("DISCORD_TOKEN:", DISCORD_TOKEN[:10])
print("MONGO_URI:", MONGO_URI)
