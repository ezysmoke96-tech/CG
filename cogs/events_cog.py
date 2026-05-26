import discord
from discord import app_commands
from discord.ext import commands
from utils import storage
import datetime

ACCENT = discord.Color.from_rgb(88, 101, 242)
DANGER = discord.Color.from_rgb(220, 53, 69)

RESTRICTED_EVENTS = ["Patrol", "Wide Patrol"]
RESTRICTED_ROLES  = ["Commander Fox", "Commander Thorn", "Lieutenant Thire"]
ALL_EVENTS = ["Patrol", "Wide Patrol", "Combat Training", "General Training", "Physical Training", "Tryout"]

AOS_DURATION_CHOICES = [
    app_commands.Choice(name="1 Day",    value="1d"),
    app_commands.Choice(name="3 Days",   value="3d"),
    app_commands.Choice(name="1 Week",   value="1w"),
    app_commands.Choice(name="2 Weeks",  value="2w"),
    app_commands.Choice(name="Permanent", value="perm"),
]

DURATION_LABELS = {"1d": "1 Day", "3d": "3 Days", "1w": "1 Week", "2w": "2 Weeks", "perm": "Permanent"}


def has_restricted_role(member: discord.Member) -> bool:
    return any(r.name in RESTRICTED_ROLES for r in member.roles)


class EventsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="host", description="Host an event.")
    @app_commands.describe(event="The event to host", link="Link to the event")
    @app_commands.choices(event=[app_commands.Choice(name=e, value=e) for e in ALL_EVENTS])
    async def host(self, interaction: discord.Interaction, event: app_commands.Choice[str], link: str):
        if event.value in RESTRICTED_EVENTS and not has_restricted_role(interaction.user):
            roles_str = ", ".join(f"**{r}**" for r in RESTRICTED_ROLES)
            embed = discord.Embed(
                description=f"Only {roles_str} may host **{event.value}**.",
                color=DANGER,
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        cfg = storage.get_setup()
        channel_id = cfg.get("event_log_channel")
        if not channel_id:
            await interaction.response.send_message("No event log channel configured. Use `/setup` first.", ephemeral=True)
            return

        channel = self.bot.get_channel(channel_id)
        if not channel:
            await interaction.response.send_message("Event log channel not found.", ephemeral=True)
            return

        embed = discord.Embed(title="Event Log", color=ACCENT, timestamp=datetime.datetime.utcnow())
        embed.description = f"Host: {interaction.user.mention}\nEvent: \"{event.value}\""
        embed.add_field(name="Link", value=link, inline=False)

        await channel.send(embed=embed)
        await interaction.response.send_message(f"Event logged in {channel.mention}.", ephemeral=True)

    @app_commands.command(name="aos", description="Place a user on Arrest on Sight.")
    @app_commands.describe(roblox_user="Roblox username", reason="Reason for AOS", time="Duration")
    @app_commands.choices(time=AOS_DURATION_CHOICES)
    @app_commands.default_permissions(manage_roles=True)
    async def aos(self, interaction: discord.Interaction, roblox_user: str, reason: str, time: app_commands.Choice[str]):
        cfg = storage.get_setup()
        channel_id = cfg.get("cg_comms_channel")
        if not channel_id:
            await interaction.response.send_message("No CG Comms channel configured. Use `/setup` first.", ephemeral=True)
            return

        channel = self.bot.get_channel(channel_id)
        if not channel:
            await interaction.response.send_message("CG Comms channel not found.", ephemeral=True)
            return

        aos_data = storage.get_aos()
        aos_data[roblox_user.lower()] = {
            "reason": reason,
            "duration": time.value,
            "issued_by": str(interaction.user),
            "issued_at": datetime.datetime.utcnow().isoformat(),
        }
        storage.save_aos(aos_data)

        embed = discord.Embed(title="Arrest on Sight", color=DANGER, timestamp=datetime.datetime.utcnow())
        embed.add_field(name="Roblox User", value=roblox_user, inline=True)
        embed.add_field(name="Duration",    value=DURATION_LABELS.get(time.value, time.value), inline=True)
        embed.add_field(name="Reason",      value=reason, inline=False)
        embed.set_footer(text=f"Issued by {interaction.user}")

        await channel.send(embed=embed)
        await interaction.response.send_message(f"AOS placed on **{roblox_user}** and posted to {channel.mention}.", ephemeral=True)

    @app_commands.command(name="groupsync", description="Sync your Roblox group rank to Discord roles.")
    async def groupsync(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="Group Sync",
            description=(
                "To sync your Roblox rank with Discord, ensure you are verified through Bloxlink or RoVer.\n"
                "Contact an administrator if syncing is not working."
            ),
            color=ACCENT,
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="rankcheck", description="Check your current Roblox group rank.")
    async def rankcheck(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="Rank Check",
            description=(
                "Use `/bgcheck` with your Roblox username to see your full rank and statistics.\n"
                "If your Discord roles do not match, use `/groupsync`."
            ),
            color=ACCENT,
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot):
    await bot.add_cog(EventsCog(bot))
