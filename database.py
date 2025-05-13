import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
client = AsyncIOMotorClient(MONGO_URI, tls=True, tlsAllowInvalidCertificates=True)
db = client["stalker"]

sellers_collection = db["tracked_sellers"]
tiers_collection = db["user_tiers"]
asins_collection = db["last_seen_asins"]

# ----- Seller Tracking -----

async def add_tracked_seller(seller_id: str, user_id: str):
    await sellers_collection.update_one(
        {"seller_id": seller_id, "user_id": user_id},
        {"$set": {"seller_id": seller_id, "user_id": user_id}},
        upsert=True
    )

async def get_tracked_sellers(user_id: str):
    cursor = sellers_collection.find({"user_id": user_id})
    results = await cursor.to_list(length=100)
    return [doc["seller_id"] for doc in results]

async def get_all_tracked_sellers():
    cursor = sellers_collection.find()
    return await cursor.to_list(length=100)

async def count_tracked_sellers(user_id: str) -> int:
    return await sellers_collection.count_documents({"user_id": user_id})

# ----- Tier Management -----

async def assign_user_tier(user_id: str, tier: str):
    await tiers_collection.update_one(
        {"user_id": user_id},
        {"$set": {"tier": tier}},
        upsert=True
    )

async def get_user_tier(user_id: str) -> str:
    result = await tiers_collection.find_one({"user_id": user_id})
    return result["tier"] if result else "free"

# ----- Keepa ASIN Tracking -----

async def get_last_seen_asins(seller_id: str):
    doc = await asins_collection.find_one({"seller_id": seller_id})
    return doc["asins"] if doc else []

async def update_last_seen_asins(seller_id: str, asins: list):
    await asins_collection.update_one(
        {"seller_id": seller_id},
        {"$set": {"asins": asins}},
        upsert=True
    )