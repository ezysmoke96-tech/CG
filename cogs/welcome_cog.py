import discord
from discord.ext import commands
from utils import storage

CORUSCANT_GUARD_GIF = "https://media.tenor.com/w4Z0YGKF-9MAAAAC/coruscant-guard-star-wars.gif"
ACCENT = discord.Color.from_rgb(88, 101, 242)


def ordinal(n: int) -> str:
    if 11 <= (n % 100) <= 13:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"


class WelcomeCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        cfg = storage.get_setup()
        channel_id = cfg.get("welcome_channel")
        if not channel_id:
            return

        channel = self.bot.get_channel(channel_id)
        if not channel:
            return

        member_count = member.guild.member_count

        embed = discord.Embed(
            title=f"Welcome to {member.guild.name}",
            description=(
                f"Hello, {member.mention}! Welcome to **{member.guild.name}**.\n"
                f"You are our **{ordinal(member_count)}** member to join."
            ),
            color=ACCENT,
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_image(url=CORUSCANT_GUARD_GIF)
        embed.set_footer(text="Coruscant Guard — Protecting the Republic")

        await channel.send(embed=embed)


async def setup(bot):
    await bot.add_cog(WelcomeCog(bot))
