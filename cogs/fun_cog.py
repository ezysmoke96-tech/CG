import discord
from discord import app_commands
from discord.ext import commands
import random
import aiohttp

ACCENT = discord.Color.from_rgb(88, 101, 242)

EIGHT_BALL_RESPONSES = [
    "It is certain.", "It is decidedly so.", "Without a doubt.", "Yes, definitely.",
    "You may rely on it.", "As I see it, yes.", "Most likely.", "Outlook good.",
    "Yes.", "Signs point to yes.", "Reply hazy, try again.", "Ask again later.",
    "Better not tell you now.", "Cannot predict now.", "Concentrate and ask again.",
    "Don't count on it.", "My reply is no.", "My sources say no.",
    "Outlook not so good.", "Very doubtful.",
]

ROASTS = [
    "You're the reason they put instructions on shampoo bottles.",
    "I'd agree with you but then we'd both be wrong.",
    "You bring everyone so much joy when you leave the room.",
    "I've seen better-looking things at the bottom of a shoe.",
    "Your secrets are always safe with me — I never listen when you talk.",
    "You're not stupid, you just have bad luck thinking.",
    "I'd call you a clown but that would be an insult to clowns.",
    "Some people are like clouds — when they disappear, it's a beautiful day.",
]

COMPLIMENTS = [
    "You are an absolute legend.",
    "Your presence brightens the entire server.",
    "You have the energy of a thousand suns.",
    "You're genuinely one of the best people here.",
    "The server wouldn't be the same without you.",
    "You always know the right thing to say.",
    "You make this place worth coming back to.",
]

JOKES = [
    "Why don't scientists trust atoms? Because they make up everything.",
    "I told my wife she was drawing her eyebrows too high. She looked surprised.",
    "Why do cows wear bells? Because their horns don't work.",
    "I'm reading a book about anti-gravity. It's impossible to put down.",
    "Did you hear about the mathematician who's afraid of negative numbers? He'll stop at nothing to avoid them.",
    "Why can't you give Elsa a balloon? She'll let it go.",
    "I used to hate facial hair, but then it grew on me.",
]

SHIP_PHRASES = [
    "are a match made in heaven.",
    "could be the greatest couple of all time.",
    "have zero chemistry.",
    "are basically soulmates.",
    "are a disaster waiting to happen.",
    "are oddly compatible somehow.",
]


class FunCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="roll", description="Roll a dice.")
    @app_commands.describe(sides="Number of sides (default: 6)")
    async def roll(self, interaction: discord.Interaction, sides: int = 6):
        result = random.randint(1, sides)
        embed = discord.Embed(description=f"You rolled **{result}** on a d{sides}.", color=ACCENT)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="coinflip", description="Flip a coin.")
    async def coinflip(self, interaction: discord.Interaction):
        result = random.choice(["Heads", "Tails"])
        embed = discord.Embed(description=f"The coin landed on **{result}**.", color=ACCENT)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="8ball", description="Ask the magic 8-ball a question.")
    @app_commands.describe(question="Your question")
    async def eightball(self, interaction: discord.Interaction, question: str):
        response = random.choice(EIGHT_BALL_RESPONSES)
        embed = discord.Embed(color=ACCENT)
        embed.add_field(name="Question", value=question, inline=False)
        embed.add_field(name="Answer",   value=response, inline=False)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="rate", description="Rate something out of 10.")
    @app_commands.describe(thing="What to rate")
    async def rate(self, interaction: discord.Interaction, thing: str):
        rating = random.randint(0, 10)
        bar = "█" * rating + "░" * (10 - rating)
        embed = discord.Embed(color=ACCENT)
        embed.add_field(name="Subject", value=thing, inline=False)
        embed.add_field(name="Rating",  value=f"**{rating}/10**  `{bar}`", inline=False)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="ship", description="Ship two users together.")
    @app_commands.describe(user1="First user", user2="Second user")
    async def ship(self, interaction: discord.Interaction, user1: discord.Member, user2: discord.Member):
        score = random.randint(0, 100)
        bar = "█" * (score // 10) + "░" * (10 - score // 10)
        phrase = random.choice(SHIP_PHRASES)
        embed = discord.Embed(title="Compatibility", color=ACCENT)
        embed.add_field(name="Pair",   value=f"{user1.mention} + {user2.mention}", inline=False)
        embed.add_field(name="Verdict", value=phrase, inline=False)
        embed.add_field(name="Score",  value=f"**{score}%**  `{bar}`", inline=False)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="roast", description="Roast a user.")
    @app_commands.describe(user="User to roast")
    async def roast(self, interaction: discord.Interaction, user: discord.Member):
        embed = discord.Embed(description=f"{user.mention}, {random.choice(ROASTS)}", color=ACCENT)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="compliment", description="Compliment a user.")
    @app_commands.describe(user="User to compliment")
    async def compliment(self, interaction: discord.Interaction, user: discord.Member):
        embed = discord.Embed(description=f"{user.mention}, {random.choice(COMPLIMENTS)}", color=ACCENT)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="meme", description="Get a random meme.")
    async def meme(self, interaction: discord.Interaction):
        await interaction.response.defer()
        sub = random.choice(["memes", "dankmemes", "me_irl"])
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"https://www.reddit.com/r/{sub}/random.json?limit=1",
                    headers={"User-Agent": "DiscordBot/1.0"},
                ) as r:
                    data = await r.json()
            post = data[0]["data"]["children"][0]["data"]
            title = post.get("title", "Meme")
            url   = post.get("url", "")
            if not url.endswith((".jpg", ".jpeg", ".png", ".gif", ".gifv")):
                await interaction.followup.send("Could not fetch a meme. Try again.")
                return
            embed = discord.Embed(title=title, color=ACCENT)
            embed.set_image(url=url)
            await interaction.followup.send(embed=embed)
        except Exception:
            await interaction.followup.send("Could not reach Reddit. Try again later.")

    @app_commands.command(name="joke", description="Get a random joke.")
    async def joke(self, interaction: discord.Interaction):
        embed = discord.Embed(description=random.choice(JOKES), color=ACCENT)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="choose", description="Choose between multiple options.")
    @app_commands.describe(options="Options separated by commas")
    async def choose(self, interaction: discord.Interaction, options: str):
        choices = [o.strip() for o in options.split(",") if o.strip()]
        if len(choices) < 2:
            await interaction.response.send_message("Please provide at least 2 options separated by commas.", ephemeral=True)
            return
        embed = discord.Embed(description=f"I choose: **{random.choice(choices)}**", color=ACCENT)
        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(FunCog(bot))
