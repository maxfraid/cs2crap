import re
import json
import requests
from typing import Tuple
import steam.steam.webauth as wa

from cs2crap.steam_bot.request_handler import bot_request2
from cs2crap.common.utils import color_print

# ==================================================================================================================================
# |                                                      STEAM BOT UTILS                                                           |
# ==================================================================================================================================


def get_auth_data(config_path: str = "cs2crap/steam_bot/config.json"):
    try:
        with open(config_path, "r", encoding="utf-8") as login_data:
            data = json.load(login_data)

        USERNAME = data["username"]
        PASSWORD = data["password"]
    except Exception as e:
        color_print("fail", "fail", f"Ошибка получения учётных данных: {e}", True)

    return USERNAME, PASSWORD


# ==================================================================================================================================


def steam_auth(USERNAME: str, PASSWORD: str) -> Tuple[requests.Session, int]:
    """
    Аутентификация на сервере Steam.

    Parameters:
        USERNAME (str): Имя пользователя Steam.
        PASSWORD (str): Пароль пользователя Steam.

    Returns:
        Tuple[requests.Session, int]: Кортеж с сессией и Steam ID пользователя.
    """

    try:
        auth = wa.WebAuth2(USERNAME, PASSWORD)
        code_provider_function = auth.login()
        session = code_provider_function

        response = bot_request2(session, "https://store.steampowered.com/", "default")

        steam_id = int(re.findall(r"profiles\/([^\"]+)\/\" aria-", response.text)[0])

        color_print("log", "create", "Авторизация успешна.", True)

        return session, steam_id
    except Exception as e:
        color_print("fail", "fail", f"Авторизация не удалась: {e}", True)
