import re
import os
import asyncio
import pandas as pd
from math import ceil
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

from cs2crap.common.request_handler import request2
from cs2crap.common.utils import color_print, read_and_fix_csv
from cs2crap.telegram_bot.telegram_notifier import message_sending, send_message
from cs2crap.csgomarket.data_loader import get_csgomarket_items_prices


# ==================================================================================================================================
# |                                                            DATA MANAGE                                                         |
# ==================================================================================================================================


def get_items_list(start: int, count: int, sort_column: str, sort_dir: str):
    """
    ### Получает данные о предметах с указанных страниц и обновляет файл new_items.csv.

    ### Parameters:
        - start (int): Начальный индекс для запросов.
        - count (int): Общее количество предметов.
        - sort_column (str): Колонка для сортировки ("price" или "popular").
        - sort_dir (str): Направление сортировки ("asc" или "desc").

    ### Returns:
        - Добавляет предметы в data/new_items.csv (создаёт, если его нет)
    """

    current_attempt = 1
    max_attempts = 3

    base_url = f"https://steamcommunity.com/market/search/render/?query=&start=@@@&count=100&search_descriptions=0&sort_column={sort_column}&sort_dir={sort_dir}&appid=730"

    df = pd.DataFrame()
    dfs = []

    percentage = 0

    for i in range(start, start + count, 100):
        current_url = base_url.replace("@@@", str(i)).replace("@@@", str(i + 100))

        color_print("status", "done", f"Подгрузка предметов:", True)
        color_print("none", "status", f"[{i + 100} / {start + count}]", False)

        # Отправка сообщений и вывод в консоль каждые 10% от общего кол-ва:
        if (ceil(i * 100 / (start + count))) % 10 == 0:
            if percentage < ceil(i * 100 / (start + count)):
                percentage = ceil(i * 100 / (start + count))

                send_message(f"📥 *Получение данных: {percentage}%* 📥")

                color_print("done", "done", "Получение данных:", True)
                color_print("none", "status", f"{percentage}%", False)

        while current_attempt <= max_attempts:
            response_content = request2(current_url, 2, 4, True)

            item_names = re.findall(r'data-hash-name=\\"([^"]+)\\"', response_content)
            item_href = re.findall(r"href=\\\"(https:[^\"]+)\"", response_content)
            image_src = re.findall(r" src=\\.(https:[^\"]+)", response_content)

            item_href = [href.replace("\\", "").replace(" ", "") for href in item_href]
            image_src = [src.replace("\\", "").replace(" ", "") for src in image_src]

            data = {
                "item_name": item_names,
                "item_href": item_href,
                "image_src": image_src,
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

    if os.path.isfile("data/new_items.csv"):
        try:
            items_df = read_and_fix_csv("data/new_items.csv")
            df = pd.concat([items_df, df], ignore_index=True)
            df = df.drop_duplicates(subset="item_name", keep="first")
        except Exception as e:
            print(f"Ошибка чтения data/new_items.csv: {e}")

    df.to_csv("data/new_items.csv", index=False, encoding="utf-8")


# ==================================================================================================================================


def get_item_id(item_href: str) -> tuple[int, str]:
    """
    Получение ID предмета по item_href.

    Parameters:
        - item_href (str): URL-адрес предмета на торговой площадке.

    Returns:
        - int: Идентификатор предмета.
        - response_content: страница с предметом для получения volume без отдельного запроса.
    """

    response_content = request2(item_href, 2, 4, False)

    id = re.findall(
        r"Market_LoadOrderSpread. ([^..]+) \);.\/\/ initial",
        response_content,
    )

    if id:
        id = int(float(id[0]))

        color_print("done", "done", "id предмета получен:", True)
        color_print("none", "status", id, False)

        return int(id), response_content
    else:
        color_print("fail", "fail", "Ошибка получения id.", True)
        return int(0), response_content


# ==================================================================================================================================


def get_item_prices(item_id: int) -> tuple[float, float]:
    """
    Получение цен предмета по его ID.

    Parameters:
        - item_id (int): ID предмета.

    Returns:
        - tuple[float, float]: Цена покупки и цена продажи.
    """

    ERROR_PRICE = -0.7

    try_count: int = 1

    while try_count < 3:
        response_content = request2(
            f"https://steamcommunity.com/market/itemordershistogram?country=RU&language=russian&currency=5&item_nameid={item_id}&two_factor=0",
            2,
            4,
            False,
        )

        prices = re.findall(r"_promote\\\">([^<>]+) ", response_content)

        # Проверка на наличие ответа и что обе цены получены
        if (response_content is not None) and (len(prices) == 2):
            prices[0] = prices[0].replace(",", ".")
            prices[1] = prices[1].replace(",", ".")

            color_print("done", "done", "Цены предмета получены.", True)
            return prices[0], prices[1]

        # Проверка если цен нет, то выполнено две попытки
        elif try_count == 2:
            color_print(
                "fail",
                "fail",
                f"Ошибка получения цен: Этот предмет никто не продаёт.",
                True,
            )
            return ERROR_PRICE, ERROR_PRICE

        try_count += 1


# ==================================================================================================================================


def get_item_volume(item_href: str = None, item_page: str = None) -> int:
    """
    Получение кол-ва продаж предмета за последние сутки.

    Parameters:
        - item_href (str): Ссылка на предмет на торговой площадке.
        - item_page (str): Уже подгруженная страница (из запроса для получения id).

    Returns:
        - int: Кол-во продаж предмета за последние 24 часа.
    """

    volume = 0

    current_time = datetime.now()
    current_date = current_time.strftime("%b %d %Y")

    back_time = current_time - timedelta(hours=24)
    formatted_back_date = back_time.strftime("%b %d %Y")

    back_hours_since = back_time.strftime("%H")

    # Если в функцию поступает страница с предметом, то запрос не кидается
    if item_page is None:
        response_content = request2(item_href, 2, 4, False)
    elif item_page is not None:
        response_content = item_page

    soup = BeautifulSoup(response_content, "html.parser")
    script_tags = soup.find_all("script")

    if script_tags:
        last_script_content = script_tags[-1].string

        current_day_pattern = re.compile(rf"{current_date}.*?\"(\d+)", re.DOTALL)
        current_day_result = current_day_pattern.findall(last_script_content)

        previous_day_pattern = re.compile(
            rf"{formatted_back_date} (\d\d): .*?\"(\d+)",
            re.DOTALL,
        )
        previous_day_result = previous_day_pattern.findall(last_script_content)

    if current_day_result:
        for match in current_day_result:
            volume += int(match)

    if previous_day_result:
        for match in previous_day_result:
            if int(match[0]) >= int(back_hours_since) - 2:
                volume += int(match[1])

    color_print("done", "done", "Популярность предмета получена:", True)
    (
        color_print("none", "status", volume, False)
        if volume >= 1
        else color_print("none", "warning", volume, False)
    )

    return volume


# ==================================================================================================================================


def double_hook(
    df: pd.DataFrame,
    STM2STM: bool = True,
    CSM2STM: bool = False,
    STM2CSM: bool = True,
    items_count: int = 0,
    stop_cscrap_event: asyncio.Event = None,
) -> None:
    """
    Функция для парсинга данных (id, объем, цены) предметов за последние сутки и отправки уведомлений.

    Parameters:
        - df (pd.DataFrame): DataFrame с данными предметов.
        - STM2STM (bool): Флаг для включения/выключения метода торговли Steam -> Steam (по умолчанию True).
        - CSM2STM (bool): Флаг для включения/выключения метода торговли CS:GO Market -> Steam (по умолчанию False).
        - STM2CSM (bool): Флаг для включения/выключения метода торговли Steam -> CS:GO Market (по умолчанию True).

    Output:
        - None
    """
    item_number = 1
    item_page = None

    for index, row in df.iterrows():
        if not stop_cscrap_event.is_set():
            color_print(
                "status", "status", f"Предмет: [{item_number} / {items_count}]", True
            )

            # Отправка сообщений и вывод в консоль каждые 10% от общего кол-ва:
            if (ceil(item_number * 100 / items_count)) % 10 == 0:
                send_message(
                    f"📡 *Сканирование: {(item_number * 100 / items_count):.0f}%* 📡"
                )

            df.at[index, "item_name"] = str(df.at[index, "item_name"]).replace(
                "&amp;", "&"
            )

            if CSM2STM or STM2CSM:
                if item_number % 80 == 0:
                    color_print(
                        "status", "status", f"Обновляем базу скинов CS:GO Market.", True
                    )
                    get_csgomarket_items_prices()

            id = row.get("id")

            if pd.notna(id) and id != 0:
                color_print("done", "done", "id предмета найден:", True)
                color_print("none", "create", id, False)
            else:
                id, item_page = get_item_id(row["item_href"])
                if pd.notna(id):
                    df.at[index, "id"] = int(id)

            # Получение популярности предмета
            if item_page is not None:
                # Если id был получен, то используем уже полученную страницу
                volume = get_item_volume(item_page=item_page)
            else:
                # Если id был найден в базе, кидаем запрос
                volume = get_item_volume(row["item_href"])
            df.at[index, "volume"] = int(volume)

            if id is not None:
                # Получение цен предмета
                price_buy, price_sell = get_item_prices(id)

                df.at[index, "price_buy"] = float(price_buy)
                df.at[index, "price_sell"] = float(price_sell)

                methods = {
                    "STM2STM": STM2STM,
                    "CSM2STM": CSM2STM,
                    "STM2CSM": STM2CSM,
                }

                # Отсеиваем предметы по популярности
                if int(volume) >= 25:
                    message_sending(
                        df.at[index, "item_name"],
                        volume,
                        price_buy,
                        price_sell,
                        df.at[index, "item_href"],
                        methods,
                    )

                df = df.astype({"id": "Int64", "volume": "Int64"}, errors="ignore")

                df.to_csv("data/updated_items.csv", index=False, encoding="utf-8")

            item_number += 1


if __name__ == "__main__":
    test_item_href = "https://steamcommunity.com/market/listings/730/AK-47%20%7C%20Slate%20%28Minimal%20Wear%29"

    test_id, test_item_page = get_item_id(test_item_href)
    test_volume = get_item_volume(item_page=test_item_page)
    test_prices = get_item_prices(test_id)
