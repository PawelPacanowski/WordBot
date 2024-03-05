import datetime


async def get_user_words(channel, user, schema: dict) -> (dict, int):
    """
    Case-insensitive

    :param channel: Discord channel
    :param user: Discord user
    :param schema: Words to count
    :return: Count of each word, total words
    """

    print(f"[{datetime.datetime.now()}] searching channel: {channel.name}")
    result = schema.copy()

    oldest_id = 0
    latest_id = 0

    all_words_counter = 0

    async for message in channel.history(limit=None, oldest_first=True):
        if message.author == user:
            oldest_id = message.id
            user_message = message.content.lower().split()

            for word in user_message:
                all_words_counter += 1

                if word in schema:
                    result[word] += 1
                    
            if oldest_id == latest_id:
                break
                    
    async for message in channel.history(limit=None, oldest_first=False):
        if message.author == user:
            latest_id = message.id
            user_message = message.content.lower().split()

            for word in user_message:
                all_words_counter += 1

                if word in schema:
                    result[word] += 1
                    
            if oldest_id == latest_id:
                break

    print(f"[{datetime.datetime.now()}] search completed in channel: {channel.name}")
    return result, all_words_counter




async def get_channel_statistics(channel, schema: dict) -> list[dict]:
    """
    Scans all channel searching for words provided in the schema. Case-insensitive.
    Does not count a word count if the count = 0 (word is not provided in the returned values).
    Returned records contain id of each user.


    :param channel: Discord channel
    :param schema: Words to count
    :return: record of each member, that ever used this channel
    """

    print(f"[{datetime.datetime.now()}] searching channel: {channel.name}")

    # all member records for this channel
    results: list[dict] = []

    async for message in channel.history(limit=None, oldest_first=False):
        if message.author.bot:
            continue

        message_author = message.author.id
        message_record = {"discord_user_id": message_author,
                          "total_flagged_words": 0,
                          "total_words": 0,
                          **schema}

        message_content = message.content.lower().split()

        for word in message_content:
            message_record["total_words"] += 1
            if word in schema.keys():
                message_record["total_flagged_words"] += 1
                message_record[word] += 1

        # must merge records if they duplicate for a user
        if len(results) == 0:
            results.append(message_record)
        else:
            for i, result in enumerate(results):
                # merging for the same member
                if result.get("discord_user_id") == message_author:
                    tmp = {**result, **message_record}
                    for key in tmp.keys():
                        if key in result and key in message_record:
                            if key != "discord_user_id":
                                tmp[key] = result[key] + message_record[key]

                    results[i] = tmp
                    break

                # if results is traversed and did not find a record for current message author, appending new record
                elif len(results) == i + 1:
                    results.append(message_record)

                # if current record in the iteration is not the record of current message author, skipping to next record
                else:
                    continue

    print(f"[{datetime.datetime.now()}] search completed in channel: {channel.name}")
    return results
