import asyncio
import discord
from discord.ext import commands
from word_bot_db import db_requests
from utility import scripts


class SlashCommands(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot

    @discord.slash_command(name="add_to_whitelist")
    async def add_to_whitelist(self, ctx, member: discord.Member):
        await ctx.respond("work in progress")


    @discord.slash_command(name="remove_from_whitelist")
    async def remove_from_whitelist(self, ctx, member: discord.Member):
        await ctx.respond("work in progress")


    @discord.slash_command(name="update_server")
    async def update_server(self, ctx):
        # heavy workload
        # scans all the server

        await ctx.defer()

        # to-do: add whitelist
        if ctx.user.id != ctx.guild.owner.id:
            await ctx.send_response("You can't use that", ephemeral=True)
            return

        flagged_words = await db_requests.get_flagged_words(discord_server_id=ctx.guild.id, dictionary=True)
        channel_list = []
        server_data = []
        guild_members = [member.id for member in ctx.guild.members]

        # must update users in case a new member joined
        await db_requests.initialize_server(ctx.guild.id, guild_members)

        # updating users flagged words for data cohesion
        await db_requests.update_users_flagged_words(ctx.guild.id)

        for channel in ctx.guild.channels:
            if isinstance(channel, discord.TextChannel):
                channel_list.append(channel)

        search_tasks = [scripts.get_channel_statistics(channel, flagged_words) for channel in channel_list]
        channel_records = await asyncio.gather(*search_tasks)

        # merging records of users from multiple channels
        for channel in channel_records:
            for user_record in channel:
                if len(server_data) == 0:
                    server_data.append(user_record)
                else:
                    for i, record in enumerate(server_data):
                        # merging record if it's the same user
                        if record.get("discord_user_id") == user_record.get("discord_user_id"):
                            tmp = {**record, **user_record}
                            for key in tmp.keys():
                                if key == "discord_user_id":
                                    continue
                                if key in record and key in user_record:
                                    tmp[key] = record[key] + user_record[key]
                            server_data[i] = tmp
                            break

                        # adding new record if did not find an existing record and traversed the list
                        elif len(server_data) == i + 1:
                            server_data.append(user_record)

                        # skipping to new record if it's not the same user
                        else:
                            continue

        await db_requests.update_server(ctx.guild.id, server_data)
        await ctx.respond("Server updated successfully")


    @discord.slash_command(name="add_flagged_words", description="Provide words with spaces between them")
    async def add_flagged_words(self, ctx, words: str):
        await ctx.defer()

        if ctx.user.id != ctx.guild.owner.id:
            await ctx.send_response("You can't use that", ephemeral=True)
            return

        word_list = words.split()

        await db_requests.add_flagged_words(ctx.guild.id, word_list)

        response = "Words: *"

        for word in word_list:
            response += f"{word}, "

        response += "* successfully flagged"
        await ctx.respond(response)


    @discord.slash_command(name="remove_flagged_words", description="Provide words with spaces between them")
    async def remove_flagged_words(self, ctx, words: str):
        await ctx.defer()

        if ctx.user.id != ctx.guild.owner.id:
            await ctx.send_response("You can't use that", ephemeral=True)
            return

        word_list = words.split()

        await db_requests.remove_flagged_words(ctx.guild.id, word_list)

        response = "Words: *"

        for word in word_list:
            response += f"{word}, "

        response += "* successfully removed from flagged words"
        await ctx.respond(response)


    @discord.slash_command(name="get_flagged_words", description="List of flagged words for this server")
    async def get_flagged_words(self, ctx):
        await ctx.defer()

        words = await db_requests.get_flagged_words(ctx.guild.id)

        response = "Here are flagged words for this server: *"

        for word in words:
            response += f"{word}, "

        response += "*"
        await ctx.respond(response)


    @discord.slash_command(name="get_server_statistics", description="All information about this server")
    async def get_server_statistics(self, ctx):
        await ctx.defer()
        guild_id = ctx.guild.id

        server_words: dict = await db_requests.get_server_flagged_words_count(guild_id)
        server_total_flagged_words: int = await db_requests.get_server_total_flagged_words(guild_id)
        server_total_words: int = await db_requests.get_server_total_words(guild_id)

        message = (f"Here are statistics for {ctx.guild.name}:\n"
                   f"Total server words: {server_total_words}\n"
                   f"Total flagged words: {server_total_flagged_words}\n")

        for key in server_words.keys():
            if server_words[key] > 0:
                message += f"{key}: {server_words[key]}\n"

        await ctx.respond(message)


    @discord.slash_command(name="get_server_word_count", description="Count of specific word for this server")
    async def get_server_word_count(self, ctx, word: str):
        await ctx.defer()
        count = await db_requests.get_server_word_count(ctx.guild.id, word)
        if count:
            await ctx.respond(f"There are **{count}** occurrences of: *{word}* in this server")
        else:
            await ctx.respond(f"*{word}* never has been said or is not flagged")



    @discord.slash_command(name="get_user_statistics", description="All information about particular member")
    async def get_user_statistics(self, ctx, member: discord.Member):
        await ctx.defer()

        if member.bot:
            await ctx.send_response("Bots are not tracked", ephemeral=True)
            return

        server_id = ctx.guild.id
        user_id = member.id

        user_words: dict = await db_requests.get_user_flagged_words_count(server_id, user_id)
        user_total_flagged_words: int = await db_requests.get_user_total_flagged_words(server_id, user_id)
        user_total_words: int = await db_requests.get_user_total_words(server_id, user_id)

        message = (f"Here are statistics for {member.mention}:\n"
                   f"Total user words: {user_total_words}\n"
                   f"Total flagged words: {user_total_flagged_words}\n")

        for key in user_words:
            if user_words[key] > 0:
                message += f"{key}: {user_words[key]}\n"

        await ctx.respond(message)



    @discord.slash_command(name="get_user_word_count")
    async def get_user_word_count(self, ctx, user: discord.User, word: str):
        await ctx.defer()
        count = await db_requests.get_user_word_count(ctx.guild.id, user.id, word)
        if count:
            await ctx.respond(f"{user.mention} said *{word}* **{count}** times :)")
        else:
            await ctx.respond(f"{user.mention} never said *{word}* or word is not flagged")


    @discord.slash_command(name="get_user_last_message", description="Most recent message with flagged words.")
    async def get_user_last_message(self, ctx, user: discord.User):
        await ctx.defer()

        if user.bot:
            await ctx.respond("Bots are not tracked", ephemeral=True)
            return

        flagged_words = await db_requests.get_flagged_words(ctx.guild.id)
        channel_list = []

        for channel in ctx.guild.channels:
            if isinstance(channel, discord.TextChannel):
                channel_list.append(channel)

        search_tasks = [scripts.get_last_channel_message(channel, user, flagged_words) for channel in channel_list]
        results = await asyncio.gather(*search_tasks)

        last_message = None
        for message in results:
            if last_message is None:
                last_message = message
            else:
                if message.created_at > last_message.created_at:
                    last_message = message

        await ctx.respond(f"{user.mention} last message on this server, containing flagged words:\n*{last_message.content}*\n"
                          f"Channel: {last_message.channel}\n"
                          f"Time: {last_message.created_at.strftime('%Y-%m-%d %H:%M:%S')}")

    @discord.slash_command(name="get_user_first_message", description="First message with flagged words")
    async def get_user_first_message(self, ctx, user: discord.User):
        await ctx.defer()

        if user.bot:
            await ctx.respond("Bots are not tracked", ephemeral=True)
            return

        flagged_words = await db_requests.get_flagged_words(ctx.guild.id)
        channel_list = []

        for channel in ctx.guild.channels:
            if isinstance(channel, discord.TextChannel):
                channel_list.append(channel)

        search_tasks = [scripts.get_first_channel_message(channel, user, flagged_words) for channel in channel_list]
        results = await asyncio.gather(*search_tasks)

        last_message = None
        for message in results:
            if last_message is None:
                last_message = message
            else:
                if message.created_at < last_message.created_at:
                    last_message = message

        await ctx.respond(f"{user.mention} first message on this server, containing flagged words:\n*{last_message.content}*\n"
                          f"Channel: {last_message.channel}\n"
                          f"Time: {last_message.created_at.strftime('%Y-%m-%d %H:%M:%S')}")

    @discord.slash_command(name="add_response", description="Bot response for a given word/sentence")
    async def add_response(self, ctx, trigger: str, response: str):
        await ctx.respond("work in progress")



def setup(bot):
    bot.add_cog(SlashCommands(bot))
