import asyncio
import datetime
import discord
from discord.ext import commands
from database_api import requests


class Events(commands.Cog):

    def __init__(self, bot: discord.Bot):
        self.bot = bot

    cooldowns: list[int] = []

    @commands.Cog.listener()
    async def on_ready(self):
        tasks = []
        for guild in self.bot.guilds:
            task = asyncio.create_task(requests.initialize_guild(guild))
            tasks.append(task)

        await asyncio.gather(*tasks)
        print(f'[{datetime.datetime.now()}] {self.bot.user} online')

    @commands.Cog.listener()
    async def on_member_join(self, member):
        await requests.create_member_profile(member.guild, member)

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        await requests.initialize_guild(guild)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return

        user_message = message.content.lower().split()
        server_flagged_words = await requests.get_flagged_words(message.guild)
        total_words = 0
        user_flagged_words = {}

        for word in user_message:
            total_words += 1
            if word in server_flagged_words.keys():
                if message.author.id not in self.cooldowns:
                    await message.channel.send("We don't say that here")
                    self.cooldowns.append(message.author.id)

                if word in user_flagged_words:
                    user_flagged_words[word] += 1
                else:
                    user_flagged_words.update({word: 1})

        await requests.update_member_flags(message.guild, message.author, user_flagged_words)
        await requests.update_member_total_words(message.guild, message.author, total_words)

        await asyncio.sleep(60)
        if message.author.id in self.cooldowns:
            self.cooldowns.remove(message.author.id)

        return


def setup(bot):
    bot.add_cog(Events(bot))
