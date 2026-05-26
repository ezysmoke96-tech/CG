import discord
from discord import app_commands
from discord.ext import commands
import aiohttp
import os
import datetime

ROBLOX_COOKIE = os.getenv("ROBLOX_COOKIE", "")
MAIN_GROUP_ID = os.getenv("ROBLOX_MAIN_GROUP_ID", "")
ALLIED_GROUP_IDS = [g.strip() for g in os.getenv("ROBLOX_ALLIED_GROUP_IDS", "").split(",") if g.strip()]
ENEMY_GROUP_IDS  = [g.strip() for g in os.getenv("ROBLOX_ENEMY_GROUP_IDS",  "").split(",") if g.strip()]

HEADERS = {
    "Cookie": f".ROBLOSECURITY={ROBLOX_COOKIE}",
    "Content-Type": "application/json",
}

MIN_BADGES   = 175
MIN_FRIENDS  = 20
MIN_FOLLOWING = 10
MIN_AGE_DAYS = 365


async def roblox_get(session: aiohttp.ClientSession, url: str) -> dict:
    async with session.get(url, headers=HEADERS) as r:
        return await r.json()


async def get_user_by_name(session, username: str):
    async with session.post(
        "https://users.roblox.com/v1/usernames/users",
        json={"usernames": [username], "excludeBannedUsers": False},
        headers=HEADERS,
    ) as r:
        data = await r.json()
        return data["data"][0] if data.get("data") else None


async def get_user_info(session, user_id: int) -> dict:
    return await roblox_get(session, f"https://users.roblox.com/v1/users/{user_id}")


async def get_user_groups(session, user_id: int) -> list:
    data = await roblox_get(session, f"https://groups.roblox.com/v1/users/{user_id}/groups/roles")
    return data.get("data", [])


async def get_friends_count(session, user_id: int) -> int:
    data = await roblox_get(session, f"https://friends.roblox.com/v1/users/{user_id}/friends/count")
    return data.get("count", 0)


async def get_followers_count(session, user_id: int) -> int:
    data = await roblox_get(session, f"https://friends.roblox.com/v1/users/{user_id}/followers/count")
    return data.get("count", 0)


async def get_following_count(session, user_id: int) -> int:
    data = await roblox_get(session, f"https://friends.roblox.com/v1/users/{user_id}/followings/count")
    return data.get("count", 0)


async def get_badge_count(session, user_id: int) -> int:
    total = 0
    cursor = ""
    for _ in range(10):
        url = f"https://badges.roblox.com/v1/users/{user_id}/badges?limit=100&sortOrder=Asc"
        if cursor:
            url += f"&cursor={cursor}"
        data = await roblox_get(session, url)
        total += len(data.get("data", []))
        cursor = data.get("nextPageCursor")
        if not cursor:
            break
    return total


async def get_gamepass_count(session, user_id: int) -> int:
    total = 0
    cursor = ""
    for _ in range(20):
        url = f"https://inventory.roblox.com/v1/users/{user_id}/assets/gamepasses?limit=100"
        if cursor:
            url += f"&cursor={cursor}"
        data = await roblox_get(session, url)
        total += len(data.get("data", []))
        cursor = data.get("nextPageCursor")
        if not cursor:
            break
    return total


async def get_group_name(session, group_id: str) -> str:
    try:
        data = await roblox_get(session, f"https://groups.roblox.com/v1/groups/{group_id}")
        return data.get("name", f"Group {group_id}")
    except Exception:
        return f"Group {group_id}"


def status(passed: bool) -> str:
    return "PASS" if passed else "FAIL"


def check_line(label: str, value, minimum, passed: bool) -> str:
    mark = "[PASS]" if passed else "[FAIL]"
    return f"{mark}  {label}: {value}  (min: {minimum})"


class RobloxCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="bgcheck", description="Background check a Roblox user.")
    @app_commands.describe(roblox_user="Roblox username to check")
    async def bgcheck(self, interaction: discord.Interaction, roblox_user: str):
        await interaction.response.defer()

        async with aiohttp.ClientSession() as session:
            user_data = await get_user_by_name(session, roblox_user)
            if not user_data:
                embed = discord.Embed(
                    title="Background Check",
                    description=f"No Roblox account found for **{roblox_user}**.",
                    color=discord.Color.from_rgb(220, 53, 69),
                )
                await interaction.followup.send(embed=embed)
                return

            user_id = user_data["id"]

            info, groups, badges, friends, followers, following, gamepasses = (
                await get_user_info(session, user_id),
                await get_user_groups(session, user_id),
                await get_badge_count(session, user_id),
                await get_friends_count(session, user_id),
                await get_followers_count(session, user_id),
                await get_following_count(session, user_id),
                await get_gamepass_count(session, user_id),
            )

        user_group_map = {str(g["group"]["id"]): g for g in groups}

        created_raw = info.get("created", "")
        if created_raw:
            created_dt = datetime.datetime.fromisoformat(created_raw.replace("Z", "+00:00"))
            age_days = (datetime.datetime.now(datetime.timezone.utc) - created_dt).days
            created_str = created_dt.strftime("%B %d, %Y")
            age_str = f"{age_days} days"
        else:
            age_days = 0
            created_str = "Unknown"
            age_str = "Unknown"

        banned = info.get("isBanned", False)
        username = info.get("name", roblox_user)
        display_name = info.get("displayName", roblox_user)
        description = info.get("description", "").strip() or "None"

        pass_badges   = badges   >= MIN_BADGES
        pass_friends  = friends  >= MIN_FRIENDS
        pass_following = following >= MIN_FOLLOWING
        pass_age      = age_days >= MIN_AGE_DAYS
        pass_banned   = not banned

        overall_pass = all([pass_badges, pass_friends, pass_following, pass_age, pass_banned])

        color = discord.Color.from_rgb(40, 167, 69) if overall_pass else discord.Color.from_rgb(220, 53, 69)

        embed = discord.Embed(
            title=f"Background Check — {username}",
            url=f"https://www.roblox.com/users/{user_id}/profile",
            color=color,
            timestamp=datetime.datetime.utcnow(),
        )

        embed.add_field(
            name="Profile",
            value=(
                f"**Username:** {username}\n"
                f"**Display Name:** {display_name}\n"
                f"**User ID:** {user_id}\n"
                f"**Banned:** {'Yes' if banned else 'No'}\n"
                f"**Description:** {description[:200]}"
            ),
            inline=False,
        )

        stats_lines = [
            check_line("Badges",    badges,    f"{MIN_BADGES}+",    pass_badges),
            check_line("Friends",   friends,   f"{MIN_FRIENDS}+",   pass_friends),
            check_line("Following", following, f"{MIN_FOLLOWING}+", pass_following),
            check_line("Account Age", age_str, f"{MIN_AGE_DAYS}+ days", pass_age),
        ]
        stats_lines += [
            f"         Followers: {followers}",
            f"         Gamepasses Owned: {gamepasses}",
            f"         Account Created: {created_str}",
            f"         Total Groups: {len(groups)}",
        ]

        embed.add_field(
            name="Statistics",
            value="```\n" + "\n".join(stats_lines) + "\n```",
            inline=False,
        )

        async with aiohttp.ClientSession() as session:
            if MAIN_GROUP_ID:
                if MAIN_GROUP_ID in user_group_map:
                    g = user_group_map[MAIN_GROUP_ID]
                    main_rank = f"{g['group']['name']} — {g['role']['name']}"
                else:
                    gname = await get_group_name(session, MAIN_GROUP_ID)
                    main_rank = f"{gname} — Not a member"
                embed.add_field(name="Main Group", value=main_rank, inline=False)

            ally_lines = []
            for gid in ALLIED_GROUP_IDS:
                if gid in user_group_map:
                    g = user_group_map[gid]
                    ally_lines.append(f"[IN]  {g['group']['name']} — {g['role']['name']}")
                else:
                    gname = await get_group_name(session, gid)
                    ally_lines.append(f"[OUT] {gname} — Not a member")
            if ally_lines:
                embed.add_field(
                    name="Allied Groups",
                    value="```\n" + "\n".join(ally_lines) + "\n```",
                    inline=False,
                )

            enemy_lines = []
            for gid in ENEMY_GROUP_IDS:
                if gid in user_group_map:
                    g = user_group_map[gid]
                    enemy_lines.append(f"[DETECTED]  {g['group']['name']} — {g['role']['name']}")
                else:
                    gname = await get_group_name(session, gid)
                    enemy_lines.append(f"[CLEAR]     {gname} — Not a member")
            if enemy_lines:
                embed.add_field(
                    name="Enemy Groups",
                    value="```\n" + "\n".join(enemy_lines) + "\n```",
                    inline=False,
                )

        verdict_text = "PASSED" if overall_pass else "FAILED"
        if not overall_pass:
            failed = []
            if not pass_badges:   failed.append(f"Badges: {badges} (need {MIN_BADGES}+)")
            if not pass_friends:  failed.append(f"Friends: {friends} (need {MIN_FRIENDS}+)")
            if not pass_following: failed.append(f"Following: {following} (need {MIN_FOLLOWING}+)")
            if not pass_age:      failed.append(f"Account Age: {age_days} days (need {MIN_AGE_DAYS}+)")
            if not pass_banned:   failed.append("Account is banned")
            verdict_detail = "\n".join(f"- {f}" for f in failed)
        else:
            verdict_detail = "All requirements met."

        embed.add_field(
            name=f"Verdict — {verdict_text}",
            value=verdict_detail,
            inline=False,
        )

        embed.set_footer(text=f"Requested by {interaction.user}")
        await interaction.followup.send(embed=embed)


async def setup(bot):
    await bot.add_cog(RobloxCog(bot))
