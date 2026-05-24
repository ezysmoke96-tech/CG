import discord
from discord import app_commands
from discord.ext import commands

GIFS = {
    "order66": "https://media.giphy.com/media/3o7bu3XilJ5BOiSGic/giphy.gif",
    "rogerroger": "https://media.giphy.com/media/l0MYEqEzwMWFCg8rm/giphy.gif",
    "hellothere": "https://media.giphy.com/media/xTiIzL67tGS1kVgQaA/giphy.gif",
}


class StarWarsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="order66", description="Execute Order 66.")
    async def order66(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="Execute Order 66",
            description=(
                "*\"The time has come. Execute Order 66.\"*\n\n"
                "Every Jedi is now an enemy of the Republic. "
                "Make sure it is done. **Good soldiers follow orders.**"
            ),
            color=discord.Color.dark_red(),
        )
        embed.set_image(url=GIFS["order66"])
        embed.set_footer(text="— Chancellor Palpatine")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="goodsoldiersfolloworders", description="Good soldiers follow orders.")
    async def goodsoldiersfolloworders(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="Good soldiers follow orders.",
            description="*\"Good soldiers follow orders.\"*\n\n— CT-5385 'Tup'",
            color=discord.Color.dark_grey(),
        )
        embed.set_footer(text="The Clone Wars")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="rogerroger", description="Roger roger!")
    async def rogerroger(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="Roger Roger!",
            description=(
                "Roger, roger!\n\n"
                "*Battle droids standing by, sir.*\n"
                "Roger, roger. ✅"
            ),
            color=discord.Color.yellow(),
        )
        embed.set_image(url=GIFS["rogerroger"])
        embed.set_footer(text="— B1 Battle Droid")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="watchthosewristrockets", description="Watch those wrist rockets!")
    async def watchthosewristrockets(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="Watch Those Wrist Rockets!",
            description=(
                "*\"Whoa, whoa, whoa! Watch those wrist rockets, Waxer!\"*\n\n"
                "— Commander Cody"
            ),
            color=discord.Color.orange(),
        )
        embed.set_footer(text="Clone Wars S2E05")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="theattemptonmylife", description="The attempt on my life has left me scarred.")
    async def theattemptonmylife(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="The Attempt on My Life...",
            description=(
                "*\"The attempt on my life has left me scarred and deformed. "
                "But I assure you, my resolve has never been stronger!\"*\n\n"
                "— Emperor Palpatine"
            ),
            color=discord.Color.dark_purple(),
        )
        embed.set_footer(text="Star Wars: Revenge of the Sith")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="itsatreasonableprice", description="I sense a disturbance in the wallet.")
    async def itsatreasonableprice(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="It's a Reasonable Price!",
            description=(
                "*\"Ahh, a Jedi. We have been waiting for you. "
                "We are happy to serve... for a reasonable price.\"*\n\n"
                "Everything has a price in the galaxy. Even freedom."
            ),
            color=discord.Color.gold(),
        )
        embed.set_footer(text="The Mandalorian")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="hellothere", description="Hello there!")
    async def hellothere(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="Hello There!",
            description=(
                "*\"Hello there!\"*\n\n"
                "— General Kenobi ⚔️"
            ),
            color=discord.Color.blue(),
        )
        embed.set_image(url=GIFS["hellothere"])
        embed.set_footer(text="— Obi-Wan Kenobi, Revenge of the Sith")
        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(StarWarsCog(bot))
