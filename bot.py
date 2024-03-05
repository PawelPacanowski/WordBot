import discord
from dotenv import dotenv_values


def run_discord_bot():
    bot = discord.Bot(intents=discord.Intents.all())
    bot.load_extension(f'cogs.events')
    bot.load_extension(f'cogs.slash_commands')
    bot.run(dotenv_values(".env").get("TOKEN"))
