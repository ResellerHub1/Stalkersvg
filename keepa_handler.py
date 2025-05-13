import os
import aiohttp
import asyncio
import logging
from database import get_all_tracked_sellers, get_last_seen_asins, update_last_seen_asins

KEEPA_API_KEY = os.getenv("KEEPA_API_KEY")
KEEPA_API_URL = "https://api.keepa.com/seller"

async def fetch_asins_for_seller(seller_id: str) -> list[str]:
    async with aiohttp.ClientSession() as session:
        params = {
            "key": KEEPA_API_KEY,
            "domain": 3,  # 3 = Amazon UK
            "seller": seller_id
        }
        try:
            async with session.get(KEEPA_API_URL, params=params) as response:
                if response.status != 200:
                    logging.warning(f"Failed to fetch ASINs for seller {seller_id}: HTTP {response.status}")
                    return []
                data = await response.json()
                return data.get("asinList", [])
        except Exception as e:
            logging.error(f"Error fetching ASINs for seller {seller_id}: {e}")
            return []

async def check_for_new_asins(bot):
    sellers = await get_all_tracked_sellers()
    for seller in sellers:
        seller_id = seller["seller_id"]
        user_id = seller["user_id"]
        logging.info(f"🔍 Fetching ASINs for seller: {seller_id}")

        current_asins = await fetch_asins_for_seller(seller_id)
        if not current_asins:
            continue

        last_seen_asins = await get_last_seen_asins(seller_id)
        new_asins = list(set(current_asins) - set(last_seen_asins))

        if new_asins:
            await update_last_seen_asins(seller_id, current_asins)
            user = await bot.fetch_user(user_id)
            if user:
                asin_list = "\n".join(f"- {asin}" for asin in new_asins)
                message = f"🆕 New ASINs found for seller `{seller_id}`:\n{asin_list}"
                try:
                    await user.send(message)
                    logging.info(f"✅ Sent new ASINs to user {user_id}")
                except Exception as e:
                    logging.error(f"Failed to send DM to user {user_id}: {e}")
        else:
            logging.info(f"✅ No new ASINs for seller {seller_id}")
