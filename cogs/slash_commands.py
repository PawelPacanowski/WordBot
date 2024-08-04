import asyncio
import discord
from discord.ext import commands
from utility import scripts
from database_api import requests


class SlashCommands(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot

    # @discord.slash_command(name="add_to_whitelist")
    # async def add_to_whitelist(self, ctx, member: discord.Member):
    #     await ctx.respond("work in progress")
    #
    # @discord.slash_command(name="remove_from_whitelist")
    # async def remove_from_whitelist(self, ctx, member: discord.Member):
    #     await ctx.respond("work in progress")

    @discord.slash_command(name="update_server")
    async def update_server(self, ctx):
        # heavy workload
        # scans all the server

        await ctx.defer()

        # to-do: add whitelist
        if ctx.user.id != ctx.guild.owner.id:
            await ctx.send_response("You can't use that", ephemeral=True)
            return

        flagged_words = await requests.get_flagged_words(ctx.guild)
        for key in flagged_words.keys():
            flagged_words[key] = 0

        channel_list = []
        server_data = []
        # guild_members = [member.id for member in ctx.guild.members]

        # must update users in case a new member joined
        await requests.initialize_guild(ctx.guild)

        # # updating users flagged words for data cohesion
        # await requests.update_member_flags(ctx.guild.id)

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

        # await requests.update_server(ctx.guild.id, server_data)
        db_tasks = []
        for member_record in server_data:
            # temporary solution
            discord_user_id = member_record["discord_user_id"]
            total_words = member_record["total_words"]
            member_record.pop("discord_user_id")
            member_record.pop("total_flagged_words")
            member_record.pop("total_words")
            print(member_record)
            task = asyncio.create_task(requests.set_member_data(ctx.guild, discord_user_id, total_words, member_record))
            db_tasks.append(task)

        await asyncio.gather(*db_tasks)
        await ctx.respond("Server updated successfully")

    @discord.slash_command(name="flag_words", description="Provide words with spaces between them")
    async def flag_words(self, ctx, words: str):
        await ctx.defer()

        if ctx.user.id != ctx.guild.owner.id:
            await ctx.send_response("You can't use that", ephemeral=True)
            return

        word_list = words.split()
        await requests.flag_words(ctx.guild, word_list)
        response = "Words: *"

        for word in word_list:
            response += f"{word}, "

        response += "* successfully flagged"
        await ctx.respond(response)

    @discord.slash_command(name="unflag_words", description="Provide words with spaces between them")
    async def unflag_words(self, ctx, words: str):
        await ctx.defer()

        if ctx.user.id != ctx.guild.owner.id:
            await ctx.send_response("You can't use that", ephemeral=True)
            return

        word_list = words.split()
        await requests.unflag_words(ctx.guild, word_list)
        response = "Words: *"

        for word in word_list:
            response += f"{word}, "

        response += "* successfully removed from flagged words"
        await ctx.respond(response)

    @discord.slash_command(name="show_flagged_words", description="List of flagged words for this server")
    async def show_flagged_words(self, ctx):
        await ctx.defer()

        words = await requests.get_flagged_words(ctx.guild)
        response = "Here are flagged words for this server: *"
        for word in words.keys():
            response += f"{word}, "

        response += "*"
        await ctx.respond(response)

    @discord.slash_command(name="get_server_statistics", description="All information about this server")
    async def get_server_statistics(self, ctx):
        await ctx.defer()

        server_profile = await requests.get_server_profile(ctx.guild)
        message = (f"Here are statistics for {ctx.guild.name}:\n"
                   f"Total server words: {server_profile['total_words']}\n"
                   f"Total flagged words: {server_profile['total_flagged_words']}\n")

        for key, value in server_profile['words'].items():
            if value > 0:
                message += f"{key}: {value}\n"

        await ctx.respond(message)

    @discord.slash_command(name="get_server_word_count", description="Count of specific word for this server")
    async def get_server_word_count(self, ctx, word: str):
        await ctx.defer()
        count = await requests.get_server_word_count(ctx.guild, word)
        if count:
            await ctx.respond(f"There are **{count}** occurrences of: *{word}* in this server")
        else:
            await ctx.respond(f"*{word}* has never been said or is not flagged")

    @discord.slash_command(name="get_user_statistics", description="All information about particular member")
    async def get_user_statistics(self, ctx, member: discord.Member):
        await ctx.defer()

        if member.bot:
            await ctx.send_response("Bots are not tracked", ephemeral=True)
            return

        member_profile = await requests.get_member_profile(ctx.guild, member)

        message = (f"Here are statistics for {member.mention}:\n"
                   f"Total user words: {member_profile['total_words']}\n"
                   f"Total flagged words: {member_profile['total_flagged_words']}\n")

        for key, value in member_profile['words'].items():
            if value > 0:
                message += f"{key}: {value}\n"

        await ctx.respond(message)

    @discord.slash_command(name="get_user_word_count")
    async def get_user_word_count(self, ctx, user: discord.User, word: str):
        await ctx.defer()
        count = await requests.get_member_word_count(ctx.guild, user, word)
        if count:
            await ctx.respond(f"{user.mention} said *{word}* **{count}** times :)")
        else:
            await ctx.respond(f"{user.mention} never said *{word}* or word is not flagged")

    # @discord.slash_command(name="get_user_last_message", description="Most recent message with flagged words.")
    # async def get_user_last_message(self, ctx, user: discord.User):
    #     await ctx.defer()
    #
    #     if user.bot:
    #         await ctx.respond("Bots are not tracked", ephemeral=True)
    #         return
    #
    #     flagged_words = await requests.get_flagged_words(ctx.guild.id)
    #     channel_list = []
    #
    #     for channel in ctx.guild.channels:
    #         if isinstance(channel, discord.TextChannel):
    #             channel_list.append(channel)
    #
    #     search_tasks = [scripts.get_last_channel_message(channel, user, flagged_words) for channel in channel_list]
    #     results = await asyncio.gather(*search_tasks)
    #
    #     last_message = None
    #     for message in results:
    #         if last_message is None:
    #             last_message = message
    #         else:
    #             if message.created_at > last_message.created_at:
    #                 last_message = message
    #
    #     await ctx.respond(f"{user.mention} last message on this server, containing flagged words:\n*{last_message.content}*\n"
    #                       f"Channel: {last_message.channel}\n"
    #                       f"Time: {last_message.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
    #
    # @discord.slash_command(name="get_user_first_message", description="First message with flagged words")
    # async def get_user_first_message(self, ctx, user: discord.User):
    #     await ctx.defer()
    #
    #     if user.bot:
    #         await ctx.respond("Bots are not tracked", ephemeral=True)
    #         return
    #
    #     flagged_words = await requests.get_flagged_words(ctx.guild.id)
    #     channel_list = []
    #
    #     for channel in ctx.guild.channels:
    #         if isinstance(channel, discord.TextChannel):
    #             channel_list.append(channel)
    #
    #     search_tasks = [scripts.get_first_channel_message(channel, user, flagged_words) for channel in channel_list]
    #     results = await asyncio.gather(*search_tasks)
    #
    #     last_message = None
    #     for message in results:
    #         if last_message is None:
    #             last_message = message
    #         else:
    #             if message.created_at < last_message.created_at:
    #                 last_message = message
    #
    #     await ctx.respond(f"{user.mention} first message on this server, containing flagged words:\n*{last_message.content}*\n"
    #                       f"Channel: {last_message.channel}\n"
    #                       f"Time: {last_message.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
    #
    # @discord.slash_command(name="add_response", description="Bot response for a given word/sentence")
    # async def add_response(self, ctx, trigger: str, response: str):
    #     await ctx.respond("work in progress")


def setup(bot):
    bot.add_cog(SlashCommands(bot))
