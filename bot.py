import os
import asyncio
import discord
from discord.ext import commands
from config import DISCORD_TOKEN
from keepa_handler import check_for_new_asins

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="/", intents=intents)

async def load_extensions():
    for filename in os.listdir("./commands"):
        if filename.endswith(".py") and filename != "__init__.py":
            await bot.load_extension(f"commands.{filename[:-3]}")

async def background_task():
    await bot.wait_until_ready()
    while not bot.is_closed():
        print("🔁 Running scheduled ASIN check...")
        await check_for_new_asins(bot)
        await asyncio.sleep(3600)  # every 1 hour

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user} (ID: {bot.user.id})")
    await bot.tree.sync()
    print("✅ Slash commands synced.")
    print("------")

async def main():
    async with bot:
        await load_extensions()
        bot.loop.create_task(background_task())
        await bot.start(DISCORD_TOKEN)

if __name__ == "__main__":
    asyncio.run(main())

