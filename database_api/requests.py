import requests
from dotenv import dotenv_values

_base_url = dotenv_values(".env").get("API_URL")


async def get_flagged_words(guild) -> dict:
    params = {"dc_server_id": guild.id}
    result = requests.get(f"{_base_url}/servers/get_flagged_words", params=params)
    return result.json()['words']


async def initialize_guild(guild):
    member_ids = [member.id for member in guild.members]
    params = {"dc_server_id": guild.id}

    # Will have status 400 if server profile already exists
    requests.post(f"{_base_url}/servers/create_profile", params=params)
    requests.post(f"{_base_url}/users/create_multiple_profiles", params=params, json=member_ids)
    return None


async def create_member_profile(guild, member):
    params = {
        "dc_server_id": guild.id,
        "dc_user_id": member.id
    }

    response = requests.post(f"{_base_url}/users/create_profile", params=params)
    if response.status_code == 200:
        return True

    return False


async def update_member_flags(guild, member, data: dict):
    if isinstance(member, int):
        params = {
            "dc_server_id": guild.id,
            "dc_user_id": member
        }

    else:
        params = {
            "dc_server_id": guild.id,
            "dc_user_id": member.id
        }

    response = requests.put(f"{_base_url}/users/update_user_flags", params=params, json=data)
    if response.status_code == 200:
        return True

    return False


async def update_member_total_words(guild, member, count: int):
    if isinstance(member, int):
        params = {
            "dc_server_id": guild.id,
            "dc_user_id": member,
            "count": count
        }

    else:
        params = {
            "dc_server_id": guild.id,
            "dc_user_id": member.id,
            "count": count
        }

    response = requests.put(f"{_base_url}/users/update_user_total_words", params=params)
    if response.status_code == 200:
        return True

    return False


async def flag_words(guild, words: list):
    params = {
        "dc_server_id": guild.id
    }

    response = requests.patch(f"{_base_url}/servers/flag_words", params=params, json=words)
    if response.status_code == 200:
        return True

    return False


async def unflag_words(guild, words: list):
    params = {
        "dc_server_id": guild.id
    }

    response = requests.patch(f"{_base_url}/servers/unflag_words", params=params, json=words)
    if response.status_code == 200:
        return True

    return False


async def get_server_profile(guild) -> dict:
    params = {
        "dc_server_id": guild.id
    }

    response = requests.get(f"{_base_url}/servers/get_profile", params=params)
    return response.json()


async def get_member_profile(guild, member) -> dict:
    params = {
        "dc_server_id": guild.id,
        "dc_user_id": member.id
    }

    response = requests.get(f"{_base_url}/servers/get_profile", params=params)
    return response.json()


async def get_server_word_count(guild, word: str) -> int:
    params = {
        "dc_server_id": guild.id,
        "word": word
    }

    response = requests.get(f"{_base_url}/servers/get_word_count", params=params)
    return response.json()['words'][word]


async def get_member_word_count(guild, member, word: str) -> int:
    params = {
        "dc_server_id": guild.id,
        "dc_user_id": member.id,
        "word": word
    }

    response = requests.get(f"{_base_url}/users/get_word_count", params=params)
    return response.json()['words'][word]


async def set_member_data(guild, member, total_words: int, flags: dict[str, int]):
    if isinstance(member, int):
        params = {
            "dc_server_id": guild.id,
            "dc_user_id": member,
            "total_words": total_words
        }

    else:
        params = {
            "dc_server_id": guild.id,
            "dc_user_id": member.id,
            "total_words": total_words
        }

    response = requests.put(f"{_base_url}/users/set_user_data", params=params, json=flags)
    if response.status_code == 200:
        return True

    return False


async def delete_member_profile(guild, member):
    params = {
        "dc_server_id": guild.id,
        "dc_user_id": member.id
    }

    response = requests.delete(f"{_base_url}/users/remove_profile", params=params)
    if response.status_code == 200:
        return True
