import re
import os
import json
import pandas as pd

from cs2crap.analytics.utils import safe_filename
from cs2crap.common.request_handler import request2
from cs2crap.common.utils import color_print, read_and_fix_csv

AGENTS_URL = "https://steamcommunity.com/market/search/render/?query=&start=@@@&count=100&search_descriptions=0&sort_column=price&sort_dir=asc&appid=730&category_730_ItemSet%5B%5D=any&category_730_ProPlayer%5B%5D=any&category_730_StickerCapsule%5B%5D=any&category_730_TournamentTeam%5B%5D=any&category_730_Type%5B%5D=tag_Type_CustomPlayer&category_730_Weapon%5B%5D=any"


# ==================================================================================================================================
# |                                                DATA MANAGE FOR PRICES ANALYTICS                                                |
# ==================================================================================================================================

def get_items_category_count(items_category: str) -> int:
    """
    Отправляет запрос и выцепляет из него количество предметов нужной категории.

    Parameters:
        - items_category (str): название категории.

    Returns:
        - items_count (int): количество предметов.
    """

    main_url = get_category_data(items_category)["main_url"]

    while True:
        response = request2(main_url, 2, 6, False)

        items_count = re.findall(r"<span id=\"searchResults_total\">([^\"]+)<\/span", response)

        if int(items_count[0]) != 0:
            break

    with open("cs2crap/analytics/data/category_data.json", "r") as category_data:
        data = json.load(category_data)
    
    data[items_category]["items_count"] = items_count[0]

    with open("cs2crap/analytics/data/category_data.json", "w") as category_data:
        json.dump(data, category_data, indent=4)

    return items_count[0]


# ==================================================================================================================================


def get_category_data(category_name: str):
    """
    Находит информацию для определённой категории предметов в файле category_data.json

    Parameters:
        - category_name (str): название категории.

    Returns:
        - category_data (str): информация необходимая для работы с категорией.
    """

    with open("cs2crap/analytics/data/category_data.json", "r") as category_data:
        data = json.load(category_data)
        if category_name in data:
            return data[category_name]
        else:
            color_print("fail", "fail", "Указанная категория не найдена", True)
            return None


# ==================================================================================================================================


def get_items_list(items_category: str, url: str, start: int = 0, count: int = 100) -> None:
    """
    Получает список предметов выбранной категории.

    Parameters:
        - items_category (str): категория предмета
        - url (str): ссылка на подгрузку категории
        - start (int): первый номер предмета по порядку отображения на тп
        - count (int): количество предметов для парсинга

    Returns:
        - None
    """

    current_attempt = 1
    max_attempts = 3

    base_url = url

    df = pd.DataFrame()
    dfs = []

    for i in range(start, start + count, 100):
        current_url = base_url.replace("@@@", str(i)).replace("@@@", str(i + 100))

        while current_attempt <= max_attempts:

            errors = 0
            while errors <= 2:
                response_content = request2(current_url, 5, 10, False)
                if "Ошибка поиска." not in response_content:
                    break

            color_print(
                "none",
                "done",
                f"Получены предметы: [{i + 100} / {start + count}]",
                True,
            )

            item_names = re.findall(r'data-hash-name=\\"([^"]+)\\"', response_content)
            item_href = re.findall(r"href=\\\"(https:[^\"]+)\"", response_content)

            item_href = [href.replace("\\", "").replace(" ", "") for href in item_href]

            data = {
                "item_name": item_names,
                "item_href": item_href,
            }

            try:
                dfs.append(pd.DataFrame(data))
                break
            except Exception as e:
                color_print(
                    "none",
                    "fail",
                    "Ошибка парсинга: Не все данные получены. Пробуем заново.",
                    True,
                )
                current_attempt += 1

    df = pd.concat(dfs, ignore_index=True)

    if os.path.isfile(f"cs2crap/analytics/data/{items_category}.csv"):
        try:
            items_df = read_and_fix_csv(f"cs2crap/analytics/data/{items_category}.csv")
            df = pd.concat([items_df, df], ignore_index=True)
            df = df.drop_duplicates(subset="item_name", keep="last")
        except Exception as e:
            print(f"Ошибка чтения {items_category}.csv: {e}")

    df.to_csv(f"cs2crap/analytics/data/{items_category}.csv", index=False, encoding="utf-8")


# ==================================================================================================================================


def get_items_price_history(items_category: str) -> None:
    """
    Проходится по созданному списку предметов и получает их данные

    Parameters:
        - items_category (str): категория предметов или же название файла .csv полученного из get_items_list()

    Returns:
        - None
    """
    items_df = pd.read_csv(f"cs2crap/analytics/data/{items_category}.csv")

    for index, row in items_df.iterrows():
        item_href = row["item_href"]

        response = request2(item_href, 2, 5, True)

        color_print('none', "status", f"[{index + 1}/{items_df.shape[0]}]", False)
        color_print('none', "create", f"{items_df.at[index, "item_name"]}", False)

        big_data = re.findall(
            r"\[\"([^\"]+ \d+): [^\"]+\",(-?\d+(\.\d+)?|\.\d+),\"(\d+)\"\]", response
        )

        data_list = [
            (data[0], f"{data[1]}{data[2] if not "." in str(data[1]) else ''}", data[3])
            for data in big_data
        ]

        item_df = pd.DataFrame(data_list, columns=["time", "price", "sell_count"])

        item_name = row["item_name"]

        if not os.path.exists(f"cs2crap/analytics/data/{items_category}"):
            os.makedirs(f"cs2crap/analytics/data/{items_category}")

        item_name = safe_filename(item_name)
        item_df.to_csv(f"cs2crap/analytics/data/{items_category}/{item_name}.csv", index=False)


# ==================================================================================================================================

if __name__ == "__main__":
    # get_items_list("agents", AGENTS_URL)
    # get_items_price_history("agents")
    print(get_items_category_count("agents"))
