import requests

from cs2crap.csgomarket.utils import find_api_key

API_KEY = find_api_key()

REQUESTS = {
    "ping": f"https://market.csgo.com/api/v2/ping?key={API_KEY}",
    "items": f"https://market.csgo.com/api/v2/items?key={API_KEY}",
}

# ==================================================================================================================================
# |                                                     CS:GO MARKET OPERATIONS                                                    |
# ==================================================================================================================================


def get_items():
    """
    Получает список ваших активных предметов на маркете:
        - выставленных на продажу (status = 1)
        - проданных и требуемых к передаче боту (status = 2)
        - купленных и ожидающих подтверждения передачи вам (status = 3)
        - купленных и готовых к передачи вам (status = 4)
    """

    url = REQUESTS["items"]
    response = requests.get(url)

    return response.json()


# ==================================================================================================================================


def ping_market():
    """Отправляет запрос на включение продаж, необходимо отправлять раз в 3 минуты."""

    url = REQUESTS["ping"]
    response = requests.get(url)

    return response.json()


# ==================================================================================================================================


if __name__ == "__main__":
    print(get_items())
