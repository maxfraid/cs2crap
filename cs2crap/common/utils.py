import time
import sys
import os
import pandas as pd
import urllib.parse
from colorama import Fore, Style, init


init()

colors = {
    "none": "",
    "status": Fore.LIGHTMAGENTA_EX,
    "done": Fore.GREEN,
    "fail": Fore.RED,
    "warning": Fore.YELLOW,
    "log": Fore.LIGHTBLACK_EX,
    "create": Fore.CYAN,
}

style = Style.BRIGHT

stamps = {
    "none": "",
    "status": "[%] ",
    "done": "[V] ",
    "fail": "[X] ",
    "warning": "[!] ",
    "log": "[$] ",
    "create": "[+] ",
}

# ==================================================================================================================================
# |                                                            UTILS                                                               |
# ==================================================================================================================================


def get_time(func):
    """
    Декоратор для замера времени выполнения функции.

    Parameters:
        - func (function): функция, время выполнения которой требуется замерить

    Returns:
        - None
    """

    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time() - start_time
        color_print("log", "log", f"Время выполнения: {end_time}", True)
        return result

    return wrapper


# ==================================================================================================================================


def escape_url(url: str) -> str:
    """Функция для экранирования специальных символов в URL."""

    return urllib.parse.quote(url, safe=":/?=&")


# ==================================================================================================================================


def color_print(stamp: str, color: str, message: str, newline: bool) -> None:
    """
    Функция для красивого вывода в консоль.

    Parameters:
        - stamp (str): штамп для определения вида сообщения.
        - color (str): цвет текста сообщения.
        - message (str): текст сообщения.
        - newline (bool): флаг, определяющий, нужно ли добавлять переход на новую строку.

    Returns:
        - None

    Используемые штампы:
        - "none": пустой штамп
        - "status": [%]
        - "done": [V]
        - "fail": [X]
        - "warning": [!]
        - "log": [$]
        - "create": [+]

    Используемые цвета:
        - "none": обычный белый цвет
        - "status": светло-пурпурный цвет
        - "done": зеленый цвет
        - "fail": красный цвет
        - "warning": желтый цвет
        - "log": светло-черный цвет
        - "create": голубой цвет

    Используемые библиотеки:
        - colorama, установка: "pip install colorama"
    """

    to_new_line = "\n" if newline else " "

    sys.stdout.write(f"{to_new_line}{style}{colors[color]}{stamps[stamp]}{message}")


# ==================================================================================================================================


def print_cscrap_logo() -> None:
    """Выводит логотип CS2CRAP в консоль с использованием цветового оформления."""

    cscrap_logo = r"""
  ___  ____  ____   ___  ____   __   ____ 
 / __)/ ___)(___ \ / __)(  _ \ / _\ (  _ \
( (__ \___ \ / __/( (__  )   //    \ ) __/
 \___)(____/(____) \___)(__\_)\_/\_/(__)  


Author: cls
Gmail: ferjenkill@gmail.com
Github: https://github.com/maxfraid/cs2crap

"""

    color_print("none", "warning", cscrap_logo, True)


# ==================================================================================================================================


def create_empty_items_csv(filename: str) -> None:
    """
    Создает пустой CSV файл с заголовками по порядку.

    Parameters:
        - filename (str): Имя файла, который нужно создать.

    Returns:
        - None
    """

    columns = [
        "id",
        "item_name",
        "price_buy",
        "price_sell",
        "volume",
        "item_href",
        "image_src",
    ]

    df = pd.DataFrame(columns=columns)
    df.to_csv(filename, index=False, encoding="utf-8")


# ==================================================================================================================================


def read_and_fix_csv(filename: str) -> pd.DataFrame:
    """
    Читает данные из CSV файла в нужном формате. Изменяет порядок столбцов.

    Parameters:
        - filename (str): Имя файла с данными предметов в формате CSV.

    Returns:
        - DataFrame: Прочитанные данные с измененным порядком столбцов.
    """

    try:
        df = pd.read_csv(
            filename,
            encoding="utf-8",
            delimiter=",",
            dtype={
                "id": int,
                "item_name": str,
                "price_buy": float,
                "price_sell": float,
                "volume": int,
                "item_href": str,
                "image_src": str,
            },
        )

        df = df[
            [
                "id",
                "item_name",
                "price_buy",
                "price_sell",
                "volume",
                "item_href",
                "image_src",
            ]
        ]

        return df

    except Exception:
        return pd.read_csv(filename, encoding="utf-8", delimiter=",")


# ==================================================================================================================================


def filter_items(
    df: pd.DataFrame,
    price_range: tuple = (0, float("inf")),
    souvenirs: bool = False,
    graffiti: bool = False,
    stickers: bool = False,
) -> pd.DataFrame:
    """
    Фильтрует данные в DataFrame по заданным параметрам.

    Parameters:
        - df (DataFrame): Исходные данные для фильтрации.
        - price_range (tuple, optional): Диапазон цен для фильтрации. По умолчанию (0, float("inf")).
        - souvenirs (bool, optional): Флаг для исключения сувенирных товаров. По умолчанию False.
        - graffiti (bool, optional): Флаг для исключения граффити. По умолчанию False.
        - stickers (bool, optional): Флаг для исключения стикеров. По умолчанию False.

    Returns:
        - DataFrame: Отфильтрованные данные.
    """

    df = df.sort_values(by="price_sell")

    if price_range is None:
        df_filtered = df[(df["price_sell"].isnull()) & (df["price_buy"].isnull())]
    else:
        # Фильтрация по диапазону цен
        df_filtered = df[
            (df["price_sell"] >= price_range[0]) & (df["price_sell"] <= price_range[1])
        ]

    # Исключение строк с вхождениями ненужных предметов
    if not souvenirs:
        df_filtered = df_filtered[
            ~df_filtered["item_name"].str.contains("Souvenir", case=False)
        ]
    if not graffiti:
        df_filtered = df_filtered[
            ~df_filtered["item_name"].str.contains("Graffiti", case=False)
        ]
    if not stickers:
        df_filtered = df_filtered[
            ~df_filtered["item_name"].str.contains("Sticker", case=False)
        ]

    # Уточняем типы данных перед сохранением
    types_mapping = {"id": pd.Int64Dtype(), "volume": pd.Int64Dtype()}
    df_filtered = df_filtered.astype(types_mapping, errors="ignore")

    return df_filtered


# ==================================================================================================================================


def csv_up_nonprices(filename: str) -> None:
    """
    Сортирует CSV файл, поднимая все пропущенные значения в столбце 'price_buy' наверх.

    Parameters:
        - filename (str): Имя файла, который нужно обновить.

    Returns:
        - None
    """

    df = read_and_fix_csv(filename)

    df["price_buy"].fillna(-1, inplace=True)
    df = df.sort_values(by="price_buy", ascending=True)
    df["price_buy"].replace(-1, pd.NA, inplace=True)

    df["id"] = df["id"].astype(float).astype("Int64")
    df["volume"] = df["volume"].astype(float).astype("Int64")

    df.to_csv(filename, index=False, encoding="utf-8")


# ==================================================================================================================================


def find_matching_items(file_path: str) -> None:
    """
    Ищет дубликаты в CSV файле по столбцу 'id' и Returnsит их на экран.

    Parameters:
        - file_path (str): Путь к файлу для поиска дубликатов.

    Returns:
        - None
    """

    try:
        df = pd.read_csv(file_path)
        # Преобразуем столбец "id" в целочисленный тип данных
        df["id"] = df["id"].astype("Int64")
        df["volume"] = df["volume"].astype("Int64")
    except Exception as e:
        print(f"Ошибка при открытии файла: {e}")
        return

    if "id" not in df.columns:
        print("Столбец 'id' не найден в файле.")
        return

    id_duplicates_mask = df.duplicated(subset=["id"], keep=False)
    matching_ids = df.loc[id_duplicates_mask, "id"].dropna()

    item_name_duplicates_mask = df.duplicated(subset=["item_name"], keep=False)
    matching_item_names = df.loc[item_name_duplicates_mask, "item_name"].dropna()

    print(f"Количество совпадений по 'id' (исключая NaN): {matching_ids.shape[0]}")
    if not matching_ids.empty:
        print(f"Схожие значения в столбце 'id':\n{matching_ids.to_string(index=False)}")

    print(f"Количество совпадений по 'item_name': {matching_item_names.shape[0]}")
    if not matching_item_names.empty:
        print(f"\n{matching_item_names.to_string(index=False)}")


# ==================================================================================================================================


def remove_duplicates_keep_last(file_path: str, output_file_path: str) -> None:
    """
    Удаляет дубликаты по столбцу 'id', оставляя последний элемент пары.

    Parameters:
        - file_path (str): Путь к исходному файлу.
        - output_file_path (str): Путь для сохранения результата.

    Returns:
        - None
    """

    try:
        df = pd.read_csv(file_path)
        # Преобразуем столбец "id" в целочисленный тип данных
        df["id"] = df["id"].astype("Int64")
        df["volume"] = df["volume"].astype("Int64")
    except Exception as e:
        print(f"Ошибка при открытии файла: {e}")
        return

    if "id" not in df.columns:
        print("Столбец 'id' не найден в файле.")
        return

    # Удаляем дубликаты, оставляя последний элемент пары
    df.drop_duplicates(subset=["id"], keep="last", inplace=True)

    try:
        # Сохраняем результат в новый файл
        df.to_csv(output_file_path, index=False)
        print(f"Удалены дубликаты. Результат сохранен в файл: {output_file_path}")
    except Exception as e:
        print(f"Ошибка при сохранении файла: {e}")


# ==================================================================================================================================


def update_items_database(new_items_file: str, items_database_file: str) -> None:
    """
    Функция для обновления базы данных предметов на основе нового файла.

    Parameters:
        - new_items_file (string): путь к файлу с новыми предметами
        - items_database_file (string): путь к файлу базы данных предметов

    Returns:
        - None

    Принцип работы:
        1. Считывание данных: Функция считывает данные из двух CSV-файлов: new_items_file и items_database_file
        2. Обновление данных: Для каждого нового предмета из new_items_file функция проверяет, присутствует ли предмет с таким же именем в базе данных.
            - Если предмет с таким именем уже есть в базе данных, его данные обновляются.
            - Если предмет с таким именем отсутствует в базе данных, он добавляется.
        3. Сохранение данных: Обновленная база данных сохраняется обратно в items_database_file.
    """

    # Считываем данные из файлов
    df_new_items = pd.read_csv(new_items_file)

    if os.path.exists(items_database_file):
        df_items_database = pd.read_csv(items_database_file)
    else:
        create_empty_items_csv(items_database_file)

    df_new_items["item_name"] = df_new_items["item_name"].str.replace("&amp;", "&")
    df_items_database["item_name"] = df_items_database["item_name"].str.replace(
        "&amp;", "&"
    )

    # Проходим по строкам нового DataFrame
    for index, new_item in df_new_items.iterrows():
        # Преобразуем id в целое число
        if new_item["id"]:
            new_item["id"] = pd.to_numeric(
                new_item["id"], errors="coerce", downcast="integer"
            )
        # Получаем имя товара из нового DataFrame
        item_name = new_item["item_name"]
        # Ищем соответствующую строку в старом DataFrame
        matching_row = df_items_database[df_items_database["item_name"] == item_name]
        # Если находим, заменяем значения
        if not matching_row.empty:
            for column in df_new_items.columns:
                if column != "item_name" and pd.notnull(new_item[column]):
                    df_items_database.loc[matching_row.index, column] = new_item[column]
        else:
            # Если не находим совпадений, добавляем новую строку в конец DataFrame

            # FIXME: FutureWarning: The behavior of DataFrame concatenation with empty or all-NA entries is deprecated.
            # In a future version, this will no longer exclude empty or all-NA columns when determining the result dtypes.
            # To retain the old behavior, exclude the relevant entries before the concat operation.

            df_items_database = df_items_database._append(
                new_item.to_frame().T, ignore_index=True
            )

    # Преобразуем столбец "id" в целочисленный тип данных
    df_items_database["id"] = df_items_database["id"].astype("Int64")
    df_items_database["volume"] = df_items_database["volume"].astype("Int64")

    # Сохраняем обновленную базу данных
    df_items_database.to_csv(items_database_file, index=False)


if __name__ == "__main__":
    # update_items_database("data/updated_items.csv", "data/items_database.csv")
    find_matching_items("data/items_database.csv")
    # remove_duplicates_keep_last("data/items_database.csv", "data/items_database_cleaned.csv")
    # print_cscrap_logo()
