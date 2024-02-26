import os
import asyncio

from cs2crap.common.utils import (
    csv_up_nonprices,
    print_cscrap_logo,
    color_print,
    create_empty_items_csv,
    filter_items,
    update_items_database,
)
from cs2crap.common.data_manage import get_items_list, double_hook, read_and_fix_csv
from cs2crap.csgomarket.data_loader import get_csgomarket_items_prices
from cs2crap.telegram_bot.telegram_notifier import send_message


stop_cscrap_event = asyncio.Event()


# ==================================================================================================================================
# |                                                                 MAIN                                                           |
# ==================================================================================================================================


def update_database(
    start_from: int = 0,
    items_count: int = 21100,
    sort_column: str = "popular",
    sort_dir: str = "desc",
) -> None:
    """
    Создает базу данных предметов, если она не существует, и заполняет ее начальными данными:
        - item_hash_name: название предмета
        - item_href: ссылка на страницу торговой площадки с этим предметом
        - image_src: ссылка на изображение предмета

    Parameters:
        - start_from (int): Начальный номер предмета (значение должно быть кратно 100).
        - items_count (int): Количество предметов для подгрузки (значение должно быть кратно 100).
        - sort_column (str): Порядок сортировки подгружаемых предметов (popular / price)
        - sort_dir (str): Способ сортировки (desc - убывание, asc - возрастание)

    Для полного сбора предметов рекомендуется оставить значения по умолчанию.

    Returns:
        None
    """

    if not os.path.isfile("data/new_items.csv"):
        create_empty_items_csv("data/new_items.csv")

    send_message("📥 *Получение данных: 0%* 📥")
    color_print("create", "create", "Получаем предметы", True)

    get_items_list(start_from, items_count, sort_column, sort_dir)

    send_message("🛠️ *Обновляем базу данных* 🛠️")
    color_print("create", "create", "Обновляем базу данных", True)

    update_items_database("data/new_items.csv", "data/items_database.csv")

    csv_up_nonprices("data/items_database.csv")

    df = filter_items(
        read_and_fix_csv("data/items_database.csv"),
        None,
        souvenirs=True,
        graffiti=True,
        stickers=True,
    )

    df["item_name"] = df["item_name"].str.replace("&amp;", "&")

    color_print(
        "status",
        "status",
        f"Найдено {len(df)} новых предметов.",
        True,
    )

    send_message(f"🆕 *Найдено: {len(df)} новых предметов* 🆕")
    send_message(f"📋 *Получение новых данных* 📋")

    double_hook(df, False, False, False, len(df), stop_cscrap_event)

    update_items_database("data/updated_items.csv", "data/items_database.csv")


# ==================================================================================================================================


def cscrap(
    price_range: tuple = (-1, float("inf")),
    STM2STM=True,
    CSM2STM=False,
    STM2CSM=False,
    stop_cscrap_event=asyncio.Event,
) -> None:
    """
    Основная функция для скрапинга данных по предметам Counter Strike 2.

    Parameters:
        - price_range (tuple): Диапазон цен для фильтрации предметов.

        Flags (optional): Выбор методов купли-продажи (Steam -> Steam, CSGO Market -> Steam, Steam -> CSGO Market).
            - STM2STM (bool): Флаг для метода Steam -> Steam.
            - CSM2STM (bool): Флаг для метода CSGO Market -> Steam.
            - STM2CSM (bool): Флаг для метода Steam -> CSGO Market.

        - stop_cscrap_event (asyncio.Event): Событие для остановки скрапинга с помощью телеграм-бота.

    Returns:
        None
    """
    if price_range is None:
        price_range = (-1, float("inf"))

    print_cscrap_logo()
    color_print("create", "create", "Получаем данные...", True)

    get_csgomarket_items_prices()

    df = filter_items(
        read_and_fix_csv("data/items_database.csv"),
        (price_range[0], price_range[1]),
    )

    price_message = (
        f"all"
        if price_range[1] == float("inf")
        else f"{price_range[0]} - {price_range[1]}"
    )
    color_print(
        "status",
        "status",
        f"В диапазоне цен: [{price_message}] найдено {len(df)} предметов.",
        True,
    )
    send_message(f"🔍 *Найдено предметов: {len(df)}* 🔍")

    double_hook(df, STM2STM, CSM2STM, STM2CSM, len(df), stop_cscrap_event)

    update_items_database("data/updated_items.csv", "data/items_database.csv")


# ==================================================================================================================================


if __name__ == "__main__":
    color_print("fail", "fail", "chaka chaka ruvi ruvi", True)

"""
_______________________________________________________________________________________________________
|                                                                                                       |
|                                                                                                       |
|                                               МЕТОДЫ:                                                 |
|                                                                                                       |
|   TODO: Автоматизировать перепродажу с CSM -> STM.                   < < < < <                        |
|   TODO: При выборе метода CSM -> STM сделать поиск по ценам в CSM.                                    |
|   TODO: Автоматизировать перепродажу STM -> STM.                                                      |
|   TODO: Обновить сравнение цен в методе STM -> CSM для долгосрочной покупки:                          |
|       1. Анализ предмета на стабильность в Steam                                                      |
|       2. ? Анализ цен на cs:go market ?                                                               |
|                                                                                                       |
|                                                                                                       |
|                                             ИСПРАВЛЕНИЯ:                                              |
|                                                                                                       |
|   FIXME: FutureWarning: The behavior of DataFrame concatenation with empty or all-NA entries is       |
|   deprecated. In a future version, this will no longer exclude empty or all-NA columns when           |
|   determining the result dtypes. To retain the old behavior, exclude the relevant entries before the  |
|   concat operation. Предупреждение вызывает cs2crap.common.utils.update_items_database                |
|                                                                                                       |
|   FIXME: После обновления всех предметов срабатывает исключение:                                      |
|   Failed to fetch updates - TelegramNetworkError: HTTP Client says - Request timeout error            |
|   Sleep for 1.000000 seconds and try again... (tryings = 0, bot id = 6940558618)                      |
|                                                                                                       |
|_______________________________________________________________________________________________________|
"""
