import requests

_base_url = "http://127.0.0.1:8000"


async def initialize_server(discord_server_id: int, users: list[int]) -> bool:
    """
    Creates profile for the server and every provided user. Should be used when bot starts its session. Does nothing if given profile already exists
    """
    requests.post(f"{_base_url}/servers/add_profile/{discord_server_id}")

    requests.post(f"{_base_url}/users/add_multiple_profiles/{discord_server_id}", json=users)

    return True


# updates server profile, based on user profiles
# must update all users first
async def update_server(discord_server_id: int, users: list[dict]) -> bool:
    """
    Updates server profile, based on user profiles. Firstly updates every user profile for this server and then, server
    profile itself. Users list must provide all up-to-date information. Designed for slash command, potentially heavy workload

    !!! IMPORTANT !!!

    - EVERY USER MUST CONTAIN: "discord_user_id" KEY
    - KEYS THAT ARE NOT FLAGGED ON THE SERVER, ARE IGNORED
    - ORDER OF THE KEYS DOES NOT MATTER
    """

    update_users = requests.put(f"{_base_url}/users/update_all_users/{discord_server_id}", json=users)

    if update_users:
        update_server = requests.put(f"{_base_url}/servers/update_profile/{discord_server_id}")

        if update_server:
            return True

    return False


async def set_server_total_words_count(discord_server_id: int, count: int) -> bool:
    requests.put(f"{_base_url}/servers/update_total_words_count/{discord_server_id}/{count}")
    return True


async def add_flagged_words(discord_server_id: int, words: list[str]) -> bool:
    """
    Adds strings from the list to words flagged on the server and corresponding users.
    Will remove whitespace characters and ignore capital letters
    """

    requests.put(f"{_base_url}/servers/add_flagged_words/{discord_server_id}", json=words)

    return True


async def remove_flagged_words(discord_server_id: int, words: list[str]) -> bool:
    """
    Removes provided words from flagged words on the server and corresponding users.
    Will remove whitespace characters and ignore capital letters
    """
    requests.delete(f"{_base_url}/servers/remove_flagged_words/{discord_server_id}", json=words)
    return True


async def get_flagged_words(discord_server_id: int, dictionary: bool = False) -> list | dict:
    """
    Returns a list or a dictionary of flagged words on the server
    """
    response = requests.get(f"{_base_url}/servers/get_flagged_words/{discord_server_id}/{dictionary}")
    return response.json()


async def get_server_word_count(discord_server_id: int, word: str) -> int:
    """
    Returns a count of a given flagged word for the server
    """
    response = requests.get(f"{_base_url}/servers/get_word_count/{discord_server_id}/{word}")
    return response.json()


async def get_server_flagged_words_count(discord_server_id: int) -> dict:
    """
    Returns a dictionary of all flagged words and their count
    """
    response = requests.get(f"{_base_url}/servers/get_flagged_words_count/{discord_server_id}")
    return response.json()


async def get_server_total_words(discord_server_id: int) -> int:
    """
    Returns total words of the server
    """
    response = requests.get(f"{_base_url}/servers/get_total_words/{discord_server_id}")
    return response.json()


async def get_server_total_flagged_words(discord_server_id: int) -> int:
    """
    Returns total flagged words of the server
    """
    response = requests.get(f"{_base_url}/servers/get_total_flagged_words/{discord_server_id}")
    return response.json()


async def create_user_profile(discord_server_id: int, discord_user_id: int) -> bool:
    """
    Creates user profile. Designed for an event when new user joins
    """
    requests.post(f"{_base_url}/users/add_profile/{discord_server_id}/{discord_user_id}")
    return True


async def add_user_flagged_words(discord_server_id: int, discord_user_id: int) -> bool:
    """
    Adds flagged words for user, based on server flagged words. Designed for an event when new user joins
    """
    requests.post(f"{_base_url}/users/add_flagged_words/{discord_server_id}/{discord_user_id}")
    return True


async def update_users_flagged_words(discord_server_id: int) -> bool:
    """
    Adds flagged words for every user on the server, based on server flagged words
    """
    requests.post(f"{_base_url}/users/update_users_flagged_words/{discord_server_id}")
    return True


async def set_user_total_words_count(discord_server_id: int, discord_user_id: int, count: int) -> bool:
    """
    Sets total words count for the user
    """
    requests.post(f"{_base_url}/users/update_total_words_count/{discord_server_id}/{discord_user_id}/{count}")
    return True


async def get_user_word_count(discord_server_id: int, discord_user_id: int, word: str) -> int:
    """
    Returns a count of a given word of the user
    """
    response = requests.get(f"{_base_url}/users/get_word_count/{discord_server_id}/{discord_user_id}/{word}")
    return response.json()


async def get_user_flagged_words_count(discord_server_id: int, discord_user_id: int) -> dict:
    """
    Returns a dictionary with every flagged word and its count, for this user
    """
    response = requests.get(f"{_base_url}/users/get_flagged_words_count/{discord_server_id}/{discord_user_id}")
    return response.json()


async def get_user_total_flagged_words(discord_server_id: int, discord_user_id: int) -> int:
    """
    Returns a count of a given word of the user
    """
    response = requests.get(f"{_base_url}/users/get_total_flagged_words/{discord_server_id}/{discord_user_id}")
    return response.json()


async def get_user_total_words(discord_server_id: int, discord_user_id: int) -> int:
    """
    Returns a count of a given word of the user
    """
    response = requests.get(f"{_base_url}/users/get_total_words/{discord_server_id}/{discord_user_id}")
    return response.json()


async def add_user_words_count(discord_server_id: int, discord_user_id: int, words: dict) -> bool:
    """
    Adds count of given words to the user profile. Supports "total_words"
    """
    requests.put(f"{_base_url}/users/add_words_count/{discord_server_id}/{discord_user_id}", json=words)
    return True


async def add_server_words_count(discord_server_id: int, words: dict) -> bool:
    """
    Adds count of given words to the user profile. Supports "total_words"
    """
    requests.put(f"{_base_url}/servers/add_words_count/{discord_server_id}", json=words)
    return True
