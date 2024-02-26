import requests
from typing import Optional
from requests.exceptions import RequestException, Timeout, ConnectTimeout

from cs2crap.telegram_bot.utils import get_bot_data
from cs2crap.common.utils import escape_url, color_print
from cs2crap.common.price_comparison import (
    stm2stm_comparison,
    csm2stm_comparison,
    stm2csm_comparison,
)


BOT_TOKEN, TELEGRAM_API_URL, CHAT_ID = get_bot_data()


# ==================================================================================================================================
# |                                                        TELEGRAM NOTIFIER                                                       |
# ==================================================================================================================================


def send_message(message: str) -> Optional[dict]:
    """
    Логика отправки сообщения ботом.

    Parameters:
        - message (str): Сообщение для отправки.

    Returns:
        - Optional[dict]: Ответ API Телеграма в формате JSON.
    """

    params = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}

    max_retries: int = 3

    for attempt in range(max_retries):
        try:
            response = requests.post(TELEGRAM_API_URL, params=params, timeout=1)
            response.raise_for_status()
            return response.json()
        except ConnectTimeout as connect_timeout_error:
            color_print(
                "fail",
                "fail",
                f"Ошибка подключения к серверу Telegram: {connect_timeout_error}",
                True,
            )
        except (RequestException, Timeout) as other_error:
            color_print(
                "fail",
                "fail",
                f"Произошла ошибка: {other_error}",
                True,
            )


# ==================================================================================================================================


def stm2stm_message(
    item_name: str, volume: int, price_buy: float, price_sell: float, item_href: str
) -> None:
    """
    Отправляет стандартное сообщение о предмете метода Steam -> Steam

    Parameters:
        - item_name (str): Название предмета.
        - volume (int): Объем продаж за сутки.
        - price_buy (float): Цена покупки.
        - price_sell (float): Цена продажи.
        - item_href (str): Ссылка на предмет.

    Returns:
        - None
    """
    send_message(
        f"""
Найден предмет: *{item_name}*

📈 Цена покупки: *{price_sell}* ₽
📉 Цена продажи: *{price_buy}* ₽
🚀 Прибыль: *{round(((float(price_buy) * 0.87) - float(price_sell)) / float(price_sell) * 100)}%*

🔥 *{volume}* продаж(и) за сутки

🧰 Метод: *Steam to Steam*

🔗 [Предмет на Steam Market]({item_href})"""
    )


# ==================================================================================================================================


def csm2stm_message(
    item_name: str,
    volume: int,
    price_buy: float,
    price_sell: float,
    item_href: str,
    result_buy: Optional[bool],
    result_sell: Optional[bool],
    csgomarket_item_price: float,
):
    """
    Отправляет сообщение о предмете метода CS:GO Market -> Steam.

    Parameters:
        - item_name (str): Название предмета.
        - volume (int): Объем продаж за сутки.
        - price_buy (float): Цена покупки.
        - price_sell (float): Цена продажи.
        - item_href (str): Ссылка на предмет.
        - result_buy (Optional[bool]): Результат проверки покупки.
        - result_sell (Optional[bool]): Результат проверки продажи.
        - csgomarket_item_price (float): Цена предмета на CS:GO Market.

    Returns:
        - None
    """

    # Экранируем ссылку на csgo market
    escaped_csgomarket_url = escape_url(
        f"https://market.csgo.com/ru/?search={item_name}"
    )

    send_message(
        f"""
Найден предмет: *{item_name}*
{'\n' + '🔥🔥🔥 *AUTOBUY* 🔥🔥🔥\n' if result_sell else ''}
📈 Цена покупки: *{csgomarket_item_price}* ₽
📉 Цена продажи: *{price_sell if result_sell else price_buy}* ₽
🚀 Прибыль: *{round(((float(price_sell) * 0.87) - csgomarket_item_price) / csgomarket_item_price * 100) if result_sell 
                else round(((float(price_buy) * 0.87) - csgomarket_item_price) / csgomarket_item_price * 100) if result_buy 
                else None}%*

🔥 *{volume}* продаж(и) в *Steam* за сутки

🧰 Метод: *CS:GO Market* to *Steam*

🔗 [Предмет на CS:GO Market]({escaped_csgomarket_url})
🔗 [Предмет на Steam Market]({item_href})"""
    )


# ==================================================================================================================================


def stm2csm_message(
    item_name: str,
    volume: int,
    price_buy: float,
    price_sell: float,
    item_href: str,
    result_buy: Optional[bool],
    result_sell: Optional[bool],
    csgomarket_item_price: float,
) -> None:
    """
    Отправляет сообщение о предмете метода Steam -> CS:GO Market.

    Parameters:
        - item_name (str): Название предмета.
        - volume (int): Объем продаж за сутки.
        - price_buy (float): Цена покупки.
        - price_sell (float): Цена продажи.
        - item_href (str): Ссылка на предмет.
        - result_buy (Optional[bool]): Результат проверки покупки.
        - result_sell (Optional[bool]): Результат проверки продажи.
        - csgomarket_item_price (float): Цена предмета на CS:GO Market.

    Returns:
        - None
    """

    # Экранируем ссылку на csgo market
    escaped_csgomarket_url = escape_url(
        f"https://market.csgo.com/ru/?search={item_name}"
    )

    send_message(
        f"""
Найден предмет: *{item_name}*
{'\n' + '🔥🔥🔥 *FAST BUY* 🔥🔥🔥\n' if result_buy else ''}
📈 Цена покупки: *{price_buy if result_buy else price_sell}* ₽
📉 Цена продажи: *{csgomarket_item_price}* ₽
🚀 Прибыль: *{round(((csgomarket_item_price * 0.95) - float(price_buy)) / float(price_buy) * 100) if result_buy  
                else round(((csgomarket_item_price * 0.95) - float(price_sell)) / float(price_sell) * 100) if result_sell 
                else None}%*

🔥 *{volume}* продаж(и) в *Steam* за сутки

🧰 Метод: *Steam* to *CS:GO Market*

🔗 [Предмет на Steam Market]({item_href})
🔗 [Предмет на CS:GO Market]({escaped_csgomarket_url})"""
    )


# ==================================================================================================================================


def message_sending(
    item_name: str,
    volume: int,
    price_buy: float,
    price_sell: float,
    item_href: str,
    methods: dict[bool, bool, bool],
) -> None:
    """
    Основная функция отправки сообщений о предмете.

    Parameters:
        - item_name (str): Название предмета.
        - volume (int): Объем продаж за сутки.
        - price_buy (float): Цена покупки.
        - price_sell (float): Цена продажи.
        - item_href (str): Ссылка на предмет.

    Returns:
        - None
    """

    result_buy = None
    result_sell = None
    csgomarket_item_price = None

    # Steam to Steam
    if methods["STM2STM"]:
        if stm2stm_comparison(price_buy, price_sell):
            stm2stm_message(item_name, volume, price_buy, price_sell, item_href)

    # CS:GO Market to Steam
    if methods["CSM2STM"]:
        result = csm2stm_comparison(item_name, price_sell, price_buy)
        if result is not None:
            (
                csgomarket_item_price,
                result_buy,
                result_sell,
            ) = result

        if result_sell or result_buy:
            csm2stm_message(
                item_name,
                volume,
                price_buy,
                price_sell,
                item_href,
                result_buy,
                result_sell,
                csgomarket_item_price,
            )

    # Steam to CS:GO Market
    if methods["STM2CSM"]:
        result = stm2csm_comparison(item_name, price_sell, price_buy)
        if result is not None:
            (csgomarket_item_price, result_buy, result_sell) = result

        if result_sell or result_buy:
            stm2csm_message(
                item_name,
                volume,
                price_buy,
                price_sell,
                item_href,
                result_buy,
                result_sell,
                csgomarket_item_price,
            )


if __name__ == "__main__":
    send_message(
        r"""
    Найден предмет: *StatTrak™ Masterminds Music Kit Box*

    🔥🔥🔥 *AUTOBUY* 🔥🔥🔥

    📈 Цена покупки: *584.75* ₽
    📉 Цена продажи: *779.92* ₽
    🚀 Прибыль: *27%*

    🔥 *12* продаж(и) в *Steam* за сутки

    🧰 Метод: *Steam* to *CS:GO Market*

    🔗 [Предмет на Steam Market](https://steamcommunity.com/market/listings/730/StatTrak%E2%84%A2%20Masterminds%20Music%20Kit%20Box)
    🔗 [Предмет на CS:GO Market](https://market.csgo.com/ru/?search=StatTrak%E2%84%A2%20Masterminds%20Music%20Kit%20Box)
    """
    )
