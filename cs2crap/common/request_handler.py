import re
import random
import requests
from time import sleep
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

from cs2crap.common.utils import color_print


# ==================================================================================================================================
# |                                                       REQUEST HANDLER DATA                                                     |
# ==================================================================================================================================

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/109.0",
    "Mozilla/5.0 (Linux; Android 11; SAMSUNG SM-G973U) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/14.2 Chrome/87.0.4280.141 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 11.1; rv:84.0) Gecko/20100101 Firefox/84.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:70.0) Gecko/20100101 Firefox/70.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 13_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.1 Mobile/15E148 Safari/604.1",
]  # Заголовки для запроса

REFERERS = [
    "https://steamcommunity.com/market/search?appid=730",
    "https://steamcommunity.com/market/search?appid=730#p2_popular_desc",
    "https://store.steampowered.com/",
    "https://forum.aerosoft.com/index.php?/topic/106743-gsdg-seychelles-v20-mesh-or-elevation-problems-at-male/",
    "https://www.allacronyms.com/GSDG",
    "https://help.steampowered.com/",
    "https://steamcommunity.com/market/listings/730/",
]  # Страницы перехода для запросов


# ==================================================================================================================================
# |                                                          REQUEST HANDLER                                                       |
# ==================================================================================================================================


def get_proxy_list() -> dict:
    """
    Получает список прокси из файла proxies.txt и возвращает словарь прокси-серверов.

    Returns:
        - dict: Словарь прокси-серверов вида {'https_1': {'https': 'http://proxy1'}, 'https_2': {'https': 'http://proxy2'}, ...}
    """

    with open("data/proxies.txt", "r", encoding="utf-8") as proxies_list:
        proxy_base = proxies_list.read().splitlines()

    proxies = {}

    for i, proxy in enumerate(proxy_base, start=1):
        proxies[f"https_{i}"] = {"https": f"http://{proxy}"}

    keys = list(proxies.keys())
    random.shuffle(keys)
    proxies = {key: proxies[key] for key in keys}

    return proxies


# ==================================================================================================================================


def get_random_user_agent() -> str:
    """
    Возвращает случайный user-agent из предоставленного списка.

    Returns:
        - str: Случайно выбранный user-agent.
    """

    return random.choice(USER_AGENTS)


# ==================================================================================================================================


def get_random_referer() -> str:
    """
    Возвращает случайный реферер из предоставленного списка.

    Returns:
        - str: Случайно выбранный реферер.
    """

    return random.choice(REFERERS)


# ==================================================================================================================================


def get_random_delay(number_from: int, number_to: int) -> float:
    """
    Генерирует случайную задержку в заданном диапазоне.

    Parameters:
        - number_from (int): Минимальное значение задержки в секундах.
        - number_to (int): Максимальное значение задержки в секундах.

    Returns:
        - float: Случайная задержка в секундах.
    """

    return random.uniform(number_from, number_to)


# ==================================================================================================================================


def get_random_proxy(proxies: dict) -> dict:
    """
    Выбирает случайный прокси из списка прокси-серверов.

    Parameters:
        - proxies (dict): Словарь прокси-серверов.

    Returns:
        - dict: Случайно выбранный прокси-сервер.
    """

    return random.choice(list(proxies.values()))


# ==================================================================================================================================


def get_session() -> requests.Session:
    """
    Создает и возвращает сессию запросов с настройками повторных попыток подключения.

    Returns:
        - requests.Session: Объект сессии для отправки HTTP-запросов.
    """

    session = requests.Session()
    retry_strategy = Retry(
        total=2,
        backoff_factor=1.5,
        status_forcelist=[500, 502, 504],
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("https://", adapter)
    return session


# ==================================================================================================================================
# |                                                         MAIN FUNCTIONS                                                         |
# ==================================================================================================================================


def request2(url: str, timeout_min: float, timeout_max: float, napping: bool) -> str:
    """
    Отправляет HTTP-запрос типа GET по указанному URL с использованием случайного прокси и user-agent.

    Parameters:
        - url (str): URL для отправки запроса.
        - timeout_min (float): Минимальное значение времени ожидания для запроса в секундах.
        - timeout_max (float): Максимальное значение времени ожидания для запроса в секундах.
        - napping (bool): Флаг, указывающий, следует ли делать задержку перед отправкой запроса.

    Returns:
        - str: Текстовое содержимое HTTP-ответа.
    """

    session = get_session()
    proxies = get_proxy_list()
    error_proxies = set()

    for proxy_name, proxy_info in proxies.items():
        if proxy_name in error_proxies:
            continue

        # color_print("log", "log", f"Used proxy: {proxy_name}:", True)

        try:
            r = session.get(
                url,
                headers={
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                    "Accept-Encoding": "gzip, deflate, br",
                    "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
                    "Cache-Control": "max-age=0",
                    # "Host": "steamcommunity.com",
                    "Referer": f"{get_random_referer()}",
                    "User-Agent": f"{get_random_user_agent()}",
                },
                timeout=get_random_delay(timeout_min, timeout_max),
                proxies=proxy_info,
            )

            if napping:
                sleep(get_random_delay(timeout_min, timeout_max) / 5)

            r.raise_for_status()
            if 200 <= r.status_code < 300:
                break
            else:
                color_print(
                    "fail",
                    "fail",
                    f"Неожиданный статус код: {r.status_code}",
                    True,
                )
                error_proxies.add(proxy_name)
                break

        except requests.exceptions.Timeout as e:
            color_print(
                "fail",
                "fail",
                f"Время ожидания превышено: {e}.",
                True,
            )
            error_proxies.add(proxy_name)

        except requests.exceptions.ConnectionError as e:
            color_print(
                "fail",
                "fail",
                f"Ошибка соединения с сервером: {e}.",
                True,
            )
            error_proxies.add(proxy_name)

        except requests.exceptions.RequestException as e:
            color_print(
                "fail",
                "fail",
                f"Ошибка запроса: {e}.",
                True,
            )
            if len(error_proxies) > 2:
                sleep(60)
            else:
                sleep(5)
            error_proxies.add(proxy_name)

    return r.text


# ==================================================================================================================================


def check_proxy_ip():
    """
    Проверяет IP-адрес сервера по запросу к сайту 2ip.ru и выводит его на экран.
    """

    test_ip = request2("https://2ip.ru", 1, 3, False)

    ip = re.findall(
        r"container__ip.>[^..]+ (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})", test_ip
    )

    print("\nIP:", ip[0])


# ==================================================================================================================================

if __name__ == "__main__":
    check_proxy_ip()
