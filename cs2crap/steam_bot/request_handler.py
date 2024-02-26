import requests

from cs2crap.common.utils import color_print
from cs2crap.common.request_handler import get_random_delay


API_HEADERS = {
    "UserAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Origin": "https://steamcommunity.com",
    "Referer": "https://steamcommunity.com/",
}

# ==================================================================================================================================
# |                                                      STEAM BOT REQUEST HANDLER                                                 |
# ==================================================================================================================================


def get_proxy(index: int = 1):
    """
    Возвращает прокси-сервер из списка прокси.

    Parameters:
        index (int): Индекс прокси-сервера в списке прокси. По умолчанию 1.

    Returns:
        dict: Прокси-сервер в формате словаря.

    Raises:
        ValueError: Если переданный индекс превышает количество доступных прокси.
    """

    with open("data/proxies.txt", "r", encoding="utf-8") as proxies_list:
        proxy_base = proxies_list.read().splitlines()

    if 1 <= index <= len(proxy_base):
        proxy = proxy_base[index - 1]
        return {"https": f"http://{proxy}"}
    else:
        raise ValueError("Неправильный индекс прокси.")


# ==================================================================================================================================


def bot_request2(session: requests.Session, url: str, type: str):
    """
    Выполняет HTTP-запрос с помощью сессии и возвращает ответ.

    Parameters:
        session (requests.Session): Сессия для выполнения запроса.
        url (str): URL-адрес запроса.
        type (str): Тип запроса.

    Returns:
        requests.Response: Ответ на запрос.
    """

    while True:
        try:
            response = session.get(
                url,
                headers=API_HEADERS,
                timeout=get_random_delay(2, 4),
                proxies=get_proxy(),
            )

            return response
        except requests.exceptions.RequestException as e:
            color_print("fail", "fail", f"Ошибка запроса: {e}", True)
