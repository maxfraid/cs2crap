import json

from cs2crap.common.utils import color_print

# ==================================================================================================================================
# |                                                      TELEGRAM BOT UTILS                                                        |
# ==================================================================================================================================


def get_bot_data(config_path: str = "cs2crap/telegram_bot/config.json"):
    """
    Находит BOT_TOKEN и CHAT_ID в config.json и подставляет значение в TELEGRAM_API_URL.

    Returns:
        - BOT_TOKEN: токен бота
        - TELEGRAM_API_URL: ссылка на API бота
        - CHAT_ID: id чата с ботом
    """

    try:
        with open(config_path, "r") as config_file:
            config_data = json.load(config_file)

        BOT_TOKEN = config_data.get("BOT_TOKEN", "")
        TELEGRAM_API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        CHAT_ID = config_data.get("CHAT_ID", "")
    except Exception as e:
        color_print("fail", "fail", f"Данные бота не найдены: {e}", True)

    return BOT_TOKEN, TELEGRAM_API_URL, CHAT_ID


# ==================================================================================================================================


if __name__ == "__main__":
    print(get_bot_data())
