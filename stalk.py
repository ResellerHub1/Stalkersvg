import discord
from discord import app_commands
from discord.ext import commands
from database import (
    add_tracked_seller,
    assign_user_tier,
    get_user_tier,
    get_tracked_sellers,
    count_tracked_sellers
)

TIERS = {
    "free": 1,
    "pro": 5,
    "elite": 10,
    "admin": float('inf'),
}

class Stalk(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="stalk", description="Track a seller for new products")
    async def stalk(self, interaction: discord.Interaction, seller_id: str):
        user_id = str(interaction.user.id)
        tier = await get_user_tier(user_id)
        max_sellers = TIERS.get(tier, 1)
        current_count = await count_tracked_sellers(user_id)

        if current_count >= max_sellers:
            await interaction.response.send_message(
                f"❌ You've reached your limit of {max_sellers} tracked sellers (tier: {tier}).",
                ephemeral=True
            )
            return

        await add_tracked_seller(seller_id, user_id)
        await interaction.response.send_message(
            f"✅ You're now tracking seller `{seller_id}`.",
            ephemeral=True
        )

    @app_commands.command(name="assigntier", description="(Admin) Assign a tier to a user")
    @app_commands.describe(user="The user to assign the tier to", tier="Tier (free, pro, elite, admin)")
    async def assigntier(self, interaction: discord.Interaction, user: discord.User, tier: str):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)
            return

        if tier not in TIERS:
            await interaction.response.send_message("❌ Invalid tier. Choose from: free, pro, elite, admin", ephemeral=True)
            return

        await assign_user_tier(str(user.id), tier)
        await interaction.response.send_message(f"✅ Assigned `{tier}` tier to {user.mention}", ephemeral=True)

    @app_commands.command(name="membership", description="Check your tier and tracking limits")
    async def membership(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)
        tier = await get_user_tier(user_id)
        max_sellers = TIERS.get(tier, 1)
        current_count = await count_tracked_sellers(user_id)

        await interaction.response.send_message(
            f"💎 Tier: `{tier}`\n📦 Sellers tracked: `{current_count}/{max_sellers}`",
            ephemeral=True
        )

    @app_commands.command(name="stalklist", description="See which sellers you're currently tracking")
    async def stalklist(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)
        sellers = await get_tracked_sellers(user_id)

        if not sellers:
            await interaction.response.send_message("📭 You're not tracking any sellers.", ephemeral=True)
        else:
            seller_list = "\n".join(f"- `{s}`" for s in sellers)
            await interaction.response.send_message(f"📦 Tracked sellers:\n{seller_list}", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(Stalk(bot))
