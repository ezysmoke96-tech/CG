import discord
from discord import app_commands
from discord.ext import commands
import aiohttp
import os
import datetime

ROBLOX_COOKIE = os.getenv("ROBLOX_COOKIE", "")
MAIN_GROUP_ID = os.getenv("ROBLOX_MAIN_GROUP_ID", "")

ALLIED_GROUP_IDS_RAW = os.getenv("ROBLOX_ALLIED_GROUP_IDS", "")
ENEMY_GROUP_IDS_RAW = os.getenv("ROBLOX_ENEMY_GROUP_IDS", "")

ALLIED_GROUP_IDS = [g.strip() for g in ALLIED_GROUP_IDS_RAW.split(",") if g.strip()]
ENEMY_GROUP_IDS = [g.strip() for g in ENEMY_GROUP_IDS_RAW.split(",") if g.strip()]

HEADERS = {
    "Cookie": f".ROBLOSECURITY={ROBLOX_COOKIE}",
    "Content-Type": "application/json",
}


async def get_user_id_by_name(session: aiohttp.ClientSession, username: str):
    async with session.post(
        "https://users.roblox.com/v1/usernames/users",
        json={"usernames": [username], "excludeBannedUsers": False},
        headers=HEADERS,
    ) as r:
        data = await r.json()
        if data.get("data"):
            return data["data"][0]
        return None


async def get_user_info(session: aiohttp.ClientSession, user_id: int):
    async with session.get(f"https://users.roblox.com/v1/users/{user_id}", headers=HEADERS) as r:
        return await r.json()


async def get_user_groups(session: aiohttp.ClientSession, user_id: int):
    async with session.get(
        f"https://groups.roblox.com/v1/users/{user_id}/groups/roles", headers=HEADERS
    ) as r:
        return await r.json()


async def get_badge_count(session: aiohttp.ClientSession, user_id: int) -> int:
    total = 0
    cursor = ""
    for _ in range(5):
        url = f"https://badges.roblox.com/v1/users/{user_id}/badges?limit=100&sortOrder=Asc"
        if cursor:
            url += f"&cursor={cursor}"
        async with session.get(url, headers=HEADERS) as r:
            data = await r.json()
        total += len(data.get("data", []))
        cursor = data.get("nextPageCursor")
        if not cursor:
            break
    return total


async def get_group_name(session: aiohttp.ClientSession, group_id: str) -> str:
    try:
        async with session.get(f"https://groups.roblox.com/v1/groups/{group_id}", headers=HEADERS) as r:
            data = await r.json()
            return data.get("name", f"Group {group_id}")
    except Exception:
        return f"Group {group_id}"


class RobloxCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="bgcheck", description="Background check a Roblox user.")
    @app_commands.describe(roblox_user="Roblox username to check")
    async def bgcheck(self, interaction: discord.Interaction, roblox_user: str):
        await interaction.response.defer()

        async with aiohttp.ClientSession() as session:
            user_data = await get_user_id_by_name(session, roblox_user)
            if not user_data:
                await interaction.followup.send(f"❌ Could not find Roblox user **{roblox_user}**.")
                return

            user_id = user_data["id"]
            info = await get_user_info(session, user_id)
            groups_resp = await get_user_groups(session, user_id)
            badge_count = await get_badge_count(session, user_id)

            groups = groups_resp.get("data", [])
            user_group_map = {str(g["group"]["id"]): g for g in groups}

            created_at = info.get("created", "")
            if created_at:
                created_dt = datetime.datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                account_age_days = (datetime.datetime.now(datetime.timezone.utc) - created_dt).days
                account_age_str = f"{account_age_days} days ({account_age_days // 365} yrs)"
            else:
                account_age_str = "Unknown"

            banned = info.get("isBanned", False)
            description = info.get("description", "").strip() or "No description."
            display_name = info.get("displayName", roblox_user)
            username = info.get("name", roblox_user)

            embed = discord.Embed(
                title=f"🔎 Background Check — {username}",
                url=f"https://www.roblox.com/users/{user_id}/profile",
                color=discord.Color.red() if banned else discord.Color.blurple(),
                timestamp=datetime.datetime.utcnow(),
            )

            embed.add_field(name="👤 Username", value=username, inline=True)
            embed.add_field(name="🏷️ Display Name", value=display_name, inline=True)
            embed.add_field(name="🆔 User ID", value=str(user_id), inline=True)
            embed.add_field(name="🚫 Banned", value="Yes ❌" if banned else "No ✅", inline=True)
            embed.add_field(name="📅 Account Age", value=account_age_str, inline=True)
            embed.add_field(name="🏅 Badges", value=str(badge_count), inline=True)
            embed.add_field(name="👥 Total Groups", value=str(len(groups)), inline=True)

            if description:
                embed.add_field(name="📝 Description", value=description[:512], inline=False)

            if MAIN_GROUP_ID and MAIN_GROUP_ID in user_group_map:
                g = user_group_map[MAIN_GROUP_ID]
                embed.add_field(
                    name=f"🏠 {g['group']['name']} (Main Group)",
                    value=g["role"]["name"],
                    inline=False,
                )
            elif MAIN_GROUP_ID:
                main_name = await get_group_name(session, MAIN_GROUP_ID)
                embed.add_field(name=f"🏠 {main_name} (Main Group)", value="Not a member", inline=False)

            if ALLIED_GROUP_IDS:
                ally_lines = []
                for gid in ALLIED_GROUP_IDS:
                    if gid in user_group_map:
                        g = user_group_map[gid]
                        ally_lines.append(f"✅ **{g['group']['name']}** — {g['role']['name']}")
                    else:
                        gname = await get_group_name(session, gid)
                        ally_lines.append(f"❌ **{gname}** — Not a member")
                if ally_lines:
                    embed.add_field(name="🤝 Allied Groups", value="\n".join(ally_lines), inline=False)

            if ENEMY_GROUP_IDS:
                enemy_lines = []
                for gid in ENEMY_GROUP_IDS:
                    if gid in user_group_map:
                        g = user_group_map[gid]
                        enemy_lines.append(f"⚠️ **{g['group']['name']}** — {g['role']['name']}")
                    else:
                        gname = await get_group_name(session, gid)
                        enemy_lines.append(f"✅ **{gname}** — Not a member")
                if enemy_lines:
                    embed.add_field(name="⚔️ Enemy Groups", value="\n".join(enemy_lines), inline=False)

            embed.set_footer(text=f"Requested by {interaction.user}")
            await interaction.followup.send(embed=embed)


async def setup(bot):
    await bot.add_cog(RobloxCog(bot))
