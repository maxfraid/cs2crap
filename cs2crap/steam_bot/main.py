from time import sleep

from cs2crap.steam_bot.request_handler import bot_request2
from cs2crap.steam_bot.utils import get_auth_data, steam_auth
from cs2crap.common.request_handler import get_random_delay
from cs2crap.common.utils import color_print, print_cscrap_logo

USERNAME, PASSWORD = get_auth_data()


# ==================================================================================================================================
# |                                                           STEAM BOT MAIN                                                       |
# ==================================================================================================================================


def bot_main():
    """Основной цикл бота."""

    print_cscrap_logo()

    session, steam_id = steam_auth(USERNAME, PASSWORD)
    sleep(get_random_delay(0.7, 2))

    try:
        inventory_response = bot_request2(
            session,
            f"https://steamcommunity.com/inventory/{steam_id}/753/6?l=russian&count=75",
            "json",
        )
        inventory_items = inventory_response.json()

        inventory = []

        if "descriptions" in inventory_items:
            descriptions = inventory_items["descriptions"]

        for description in descriptions:
            market_hash_name = description.get("market_hash_name")
            if market_hash_name:
                inventory.append(market_hash_name)

        color_print("done", "done", "Инвентарь получен: ", True)
        for i in range(0, len(inventory)):
            color_print("none", "status", f"{i + 1}) {inventory[i]}", True)
    finally:
        session.close()


# ==================================================================================================================================


if __name__ == "__main__":
    bot_main()


# TODO: Сделать авторизацию сразу через прокси.
