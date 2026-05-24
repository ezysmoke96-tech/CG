import discord
from discord import app_commands
from discord.ext import commands
from utils import storage
import datetime


async def log_action(bot, action: str, moderator: discord.Member, target, reason: str, extra: str = ""):
    cfg = storage.get_setup()
    channel_id = cfg.get("mod_log_channel")
    if not channel_id:
        return
    channel = bot.get_channel(channel_id)
    if not channel:
        return
    embed = discord.Embed(
        title=f"🛡️ {action}",
        color=discord.Color.orange(),
        timestamp=datetime.datetime.utcnow(),
    )
    embed.add_field(name="Target", value=str(target), inline=True)
    embed.add_field(name="Moderator", value=moderator.mention, inline=True)
    embed.add_field(name="Reason", value=reason or "No reason provided", inline=False)
    if extra:
        embed.add_field(name="Details", value=extra, inline=False)
    await channel.send(embed=embed)


class ModerationCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ping", description="Check the bot's latency.")
    async def ping(self, interaction: discord.Interaction):
        latency = round(self.bot.latency * 1000)
        await interaction.response.send_message(f"🏓 Pong! Latency: **{latency}ms**")

    @app_commands.command(name="help", description="View all available commands.")
    async def help(self, interaction: discord.Interaction):
        embed = discord.Embed(title="📖 Command List", color=discord.Color.blurple())

        embed.add_field(name="⚙️ Setup", value=(
            "`/setup` — Configure the bot\n"
            "`/editsetup` — Edit configuration\n"
            "`/medals` — View all medals\n"
            "`/assignmedal` — Award a medal to a user"
        ), inline=False)

        embed.add_field(name="📅 Events", value=(
            "`/host <event> <link>` — Host an event\n"
            "`/groupsync` — Sync Roblox group roles\n"
            "`/rankcheck` — Check your Roblox rank"
        ), inline=False)

        embed.add_field(name="🔍 Roblox", value=(
            "`/bgcheck <user>` — Background check a Roblox user\n"
            "`/aos <user> <reason> <time>` — Arrest On Sight"
        ), inline=False)

        embed.add_field(name="🛡️ Moderation", value=(
            "`/purge` `/kick` `/ban` `/mute` `/unmute`\n"
            "`/slowmode` `/role` `/promote` `/demote`\n"
            "`/loa` `/blacklist` `/unblacklist`\n"
            "`/announce` `/lockdown` `/unlockdown`\n"
            "`/strike`"
        ), inline=False)

        embed.add_field(name="🎮 Fun", value=(
            "`/roll` `/coinflip` `/8ball` `/rate` `/ship`\n"
            "`/roast` `/compliment` `/meme` `/joke` `/choose`"
        ), inline=False)

        embed.add_field(name="⭐ Star Wars", value=(
            "`/order66` `/goodsoldiersfolloworders` `/rogerroger`\n"
            "`/watchthosewristrockets` `/theattemptonmylife`\n"
            "`/itsatreasonableprice` `/hellothere`"
        ), inline=False)

        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="purge", description="Delete a number of messages from this channel.")
    @app_commands.describe(amount="Number of messages to delete (1–100)")
    @app_commands.default_permissions(manage_messages=True)
    async def purge(self, interaction: discord.Interaction, amount: app_commands.Range[int, 1, 100]):
        await interaction.response.defer(ephemeral=True)
        deleted = await interaction.channel.purge(limit=amount)
        await interaction.followup.send(f"🗑️ Deleted **{len(deleted)}** messages.", ephemeral=True)

    @app_commands.command(name="kick", description="Kick a member from the server.")
    @app_commands.describe(user="User to kick", reason="Reason for the kick")
    @app_commands.default_permissions(kick_members=True)
    async def kick(self, interaction: discord.Interaction, user: discord.Member, reason: str = "No reason provided"):
        await user.kick(reason=reason)
        await interaction.response.send_message(f"👢 **{user}** has been kicked. Reason: {reason}")
        await log_action(self.bot, "Kick", interaction.user, user, reason)

    @app_commands.command(name="ban", description="Ban a member from the server.")
    @app_commands.describe(user="User to ban", reason="Reason for the ban")
    @app_commands.default_permissions(ban_members=True)
    async def ban(self, interaction: discord.Interaction, user: discord.Member, reason: str = "No reason provided"):
        await user.ban(reason=reason)
        await interaction.response.send_message(f"🔨 **{user}** has been banned. Reason: {reason}")
        await log_action(self.bot, "Ban", interaction.user, user, reason)

    @app_commands.command(name="mute", description="Timeout (mute) a member.")
    @app_commands.describe(user="User to mute", time="Duration in minutes")
    @app_commands.default_permissions(moderate_members=True)
    async def mute(self, interaction: discord.Interaction, user: discord.Member, time: int = 10):
        until = discord.utils.utcnow() + datetime.timedelta(minutes=time)
        await user.timeout(until, reason=f"Muted by {interaction.user}")
        await interaction.response.send_message(f"🔇 **{user}** has been muted for **{time}** minutes.")
        await log_action(self.bot, "Mute", interaction.user, user, f"Muted for {time} minutes")

    @app_commands.command(name="unmute", description="Remove timeout from a member.")
    @app_commands.describe(user="User to unmute")
    @app_commands.default_permissions(moderate_members=True)
    async def unmute(self, interaction: discord.Interaction, user: discord.Member):
        await user.timeout(None)
        await interaction.response.send_message(f"🔊 **{user}** has been unmuted.")
        await log_action(self.bot, "Unmute", interaction.user, user, "Unmuted")

    @app_commands.command(name="slowmode", description="Set slowmode for the current channel.")
    @app_commands.describe(seconds="Slowmode delay in seconds (0 to disable)")
    @app_commands.default_permissions(manage_channels=True)
    async def slowmode(self, interaction: discord.Interaction, seconds: app_commands.Range[int, 0, 21600]):
        await interaction.channel.edit(slowmode_delay=seconds)
        if seconds == 0:
            await interaction.response.send_message("⏱️ Slowmode disabled.")
        else:
            await interaction.response.send_message(f"⏱️ Slowmode set to **{seconds}** seconds.")

    @app_commands.command(name="role", description="Add or remove a role from a user.")
    @app_commands.describe(user="Target user", role="Role to add or remove")
    @app_commands.default_permissions(manage_roles=True)
    async def role(self, interaction: discord.Interaction, user: discord.Member, role: discord.Role):
        if role in user.roles:
            await user.remove_roles(role)
            await interaction.response.send_message(f"➖ Removed **{role.name}** from {user.mention}.")
        else:
            await user.add_roles(role)
            await interaction.response.send_message(f"➕ Added **{role.name}** to {user.mention}.")
        await log_action(self.bot, "Role Update", interaction.user, user, f"Role: {role.name}")

    @app_commands.command(name="promote", description="Promote a user to a specific rank/role.")
    @app_commands.describe(user="User to promote", rank="Role to promote to")
    @app_commands.default_permissions(manage_roles=True)
    async def promote(self, interaction: discord.Interaction, user: discord.Member, rank: discord.Role):
        await user.add_roles(rank)
        embed = discord.Embed(
            title="⬆️ Promotion",
            description=f"{user.mention} has been promoted to **{rank.name}**!",
            color=discord.Color.green(),
        )
        embed.set_footer(text=f"Promoted by {interaction.user}")
        await interaction.response.send_message(embed=embed)
        await log_action(self.bot, "Promotion", interaction.user, user, f"Promoted to {rank.name}")

    @app_commands.command(name="demote", description="Demote a user from a specific rank/role.")
    @app_commands.describe(user="User to demote", rank="Role to remove")
    @app_commands.default_permissions(manage_roles=True)
    async def demote(self, interaction: discord.Interaction, user: discord.Member, rank: discord.Role):
        await user.remove_roles(rank)
        embed = discord.Embed(
            title="⬇️ Demotion",
            description=f"{user.mention} has been demoted from **{rank.name}**.",
            color=discord.Color.red(),
        )
        embed.set_footer(text=f"Demoted by {interaction.user}")
        await interaction.response.send_message(embed=embed)
        await log_action(self.bot, "Demotion", interaction.user, user, f"Demoted from {rank.name}")

    @app_commands.command(name="loa", description="Put a user on Leave of Absence.")
    @app_commands.describe(user="User going on LOA", days="Number of days")
    @app_commands.default_permissions(manage_roles=True)
    async def loa(self, interaction: discord.Interaction, user: discord.Member, days: int):
        loa_data = storage.get_loa()
        uid = str(user.id)
        end_date = (datetime.datetime.utcnow() + datetime.timedelta(days=days)).strftime("%Y-%m-%d")
        loa_data[uid] = {"days": days, "end_date": end_date, "approved_by": interaction.user.id}
        storage.save_loa(loa_data)
        embed = discord.Embed(
            title="🌴 Leave of Absence",
            description=f"{user.mention} is on LOA for **{days} days** (until {end_date}).",
            color=discord.Color.yellow(),
        )
        embed.set_footer(text=f"Approved by {interaction.user}")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="blacklist", description="Blacklist a user.")
    @app_commands.describe(user="User to blacklist", reason="Reason for blacklist")
    @app_commands.default_permissions(administrator=True)
    async def blacklist(self, interaction: discord.Interaction, user: discord.Member, reason: str):
        bl = storage.get_blacklist()
        bl[str(user.id)] = {"reason": reason, "by": interaction.user.id, "username": str(user)}
        storage.save_blacklist(bl)
        embed = discord.Embed(
            title="🚫 Blacklisted",
            description=f"{user.mention} has been blacklisted.",
            color=discord.Color.dark_red(),
        )
        embed.add_field(name="Reason", value=reason)
        await interaction.response.send_message(embed=embed)
        await log_action(self.bot, "Blacklist", interaction.user, user, reason)

    @app_commands.command(name="unblacklist", description="Remove a user from the blacklist.")
    @app_commands.describe(user="User to unblacklist")
    @app_commands.default_permissions(administrator=True)
    async def unblacklist(self, interaction: discord.Interaction, user: discord.Member):
        bl = storage.get_blacklist()
        if str(user.id) not in bl:
            await interaction.response.send_message(f"**{user}** is not on the blacklist.", ephemeral=True)
            return
        bl.pop(str(user.id))
        storage.save_blacklist(bl)
        await interaction.response.send_message(f"✅ **{user}** has been removed from the blacklist.")
        await log_action(self.bot, "Unblacklist", interaction.user, user, "Removed from blacklist")

    @app_commands.command(name="announce", description="Send an announcement embed.")
    @app_commands.describe(message="The announcement message")
    @app_commands.default_permissions(manage_messages=True)
    async def announce(self, interaction: discord.Interaction, message: str):
        embed = discord.Embed(
            title="📢 Announcement",
            description=message,
            color=discord.Color.blue(),
            timestamp=datetime.datetime.utcnow(),
        )
        embed.set_footer(text=f"Announced by {interaction.user}")
        await interaction.channel.send(embed=embed)
        await interaction.response.send_message("✅ Announcement sent.", ephemeral=True)

    @app_commands.command(name="lockdown", description="Lock the current channel.")
    @app_commands.describe(reason="Reason for the lockdown")
    @app_commands.default_permissions(manage_channels=True)
    async def lockdown(self, interaction: discord.Interaction, reason: str = "No reason provided"):
        overwrite = interaction.channel.overwrites_for(interaction.guild.default_role)
        overwrite.send_messages = False
        await interaction.channel.set_permissions(interaction.guild.default_role, overwrite=overwrite)
        embed = discord.Embed(
            title="🔒 Channel Locked",
            description=f"This channel has been locked.\nReason: {reason}",
            color=discord.Color.red(),
        )
        await interaction.response.send_message(embed=embed)
        await log_action(self.bot, "Lockdown", interaction.user, interaction.channel, reason)

    @app_commands.command(name="unlockdown", description="Unlock the current channel.")
    @app_commands.default_permissions(manage_channels=True)
    async def unlockdown(self, interaction: discord.Interaction):
        overwrite = interaction.channel.overwrites_for(interaction.guild.default_role)
        overwrite.send_messages = None
        await interaction.channel.set_permissions(interaction.guild.default_role, overwrite=overwrite)
        embed = discord.Embed(
            title="🔓 Channel Unlocked",
            description="This channel has been unlocked.",
            color=discord.Color.green(),
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="strike", description="Issue a strike to a user.")
    @app_commands.describe(user="User to strike")
    @app_commands.default_permissions(manage_roles=True)
    async def strike(self, interaction: discord.Interaction, user: discord.Member):
        strikes = storage.get_strikes()
        uid = str(user.id)
        count = strikes.get(uid, {}).get("count", 0) + 1
        strikes[uid] = {"count": count, "username": str(user)}
        storage.save_strikes(strikes)

        labels = {1: "Strike 1 ⚠️", 2: "Strike 2 ⚠️⚠️", 3: "Strike 3 ❌"}
        label = labels.get(count, f"Strike {count}")

        embed = discord.Embed(
            title=f"⚠️ {label}",
            description=f"{user.mention} has received **{label}**.",
            color=discord.Color.orange() if count < 3 else discord.Color.red(),
        )
        embed.set_footer(text=f"Issued by {interaction.user}")
        await interaction.response.send_message(embed=embed)
        await log_action(self.bot, f"Strike ({count})", interaction.user, user, f"Strike {count} issued")


async def setup(bot):
    await bot.add_cog(ModerationCog(bot))
