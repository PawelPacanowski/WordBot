import asyncio
import datetime

import discord
from discord.ext import commands
from word_bot_db import db_requests






class Events(commands.Cog):

    def __init__(self, bot: discord.Bot):
        self.bot = bot

    cooldowns: list[int] = []

    @commands.Cog.listener()

    async def on_ready(self):
        guilds = self.bot.guilds

        for guild in guilds:
            member_list = guild.members
            member_ids = [member.id for member in member_list]
            await db_requests.initialize_server(guild.id, member_ids)

        print(f'[{datetime.datetime.now()}] {self.bot.user} online')


    @commands.Cog.listener()
    async def on_member_join(self, member):
        await db_requests.create_user_profile(member.guild.id, member.id)
        await db_requests.add_user_flagged_words(member.guild.id, member.id)


    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        member_list = guild.members
        member_ids = [member.id for member in member_list]
        await db_requests.initialize_server(guild.id, member_ids)


    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return

        user_message = message.content.lower().split()
        flagged_words = await db_requests.get_flagged_words(message.guild.id)
        message_record = {"total_words": 0}

        for word in user_message:
            message_record["total_words"] += 1
            if word in flagged_words:
                if message.author.id not in self.cooldowns:
                    await message.channel.send("We don't say that here")
                    self.cooldowns.append(message.author.id)

                if word in message_record:
                    message_record[word] += 1
                else:
                    message_record.update({word: 1})

        await db_requests.add_server_words_count(message.guild.id, message_record)
        await db_requests.add_user_words_count(message.guild.id, message.author.id, message_record)

        await asyncio.sleep(60)
        if message.author.id in self.cooldowns:
            self.cooldowns.remove(message.author.id)

        return




def setup(bot):
    bot.add_cog(Events(bot))
    
