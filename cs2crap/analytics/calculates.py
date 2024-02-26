import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from statsmodels.tsa.arima.model import ARIMA

from cs2crap.common.request_handler import request2


# ==================================================================================================================================
# |                                                   CALCULATES FOR PRICES ANALYTICS                                              |
# ==================================================================================================================================


def get_currency_mult() -> float:
    usd_response = request2(
        "https://steamcommunity.com/market/itemordershistogram?country=RU&language=russian&currency=1&item_nameid=176000356&two_factor=0",
        3,
        5,
        False,
    )
    rub_response = request2(
        "https://steamcommunity.com/market/itemordershistogram?country=RU&language=russian&currency=5&item_nameid=176000356&two_factor=0",
        3,
        5,
        False,
    )

    usd_prices = re.findall(r"_promote\\\">\$([^<>]+)<\\\/", usd_response)
    if (usd_response is not None) and (len(usd_prices) == 2):
        usd_prices[0] = float(
            usd_prices[0].replace(",", "").replace(".", ".", 1).replace(".", "")
        )
        usd_prices[1] = float(
            usd_prices[1].replace(",", "").replace(".", ".", 1).replace(".", "")
        )

    rub_prices = re.findall(r"_promote\\\">([^<>]+) ", rub_response)
    if (rub_response is not None) and (len(rub_prices) == 2):
        rub_prices[0] = float(
            rub_prices[0].replace(",", "").replace(".", ".", 1).replace(".", "")
        )
        rub_prices[1] = float(
            rub_prices[1].replace(",", "").replace(".", ".", 1).replace(".", "")
        )

    return ((usd_prices[0] / rub_prices[0]) + (usd_prices[1] / rub_prices[1])) / 2


# ==================================================================================================================================


def analysis(item_category: str, item_prices_filename: str):
    df = pd.read_csv(
        f"cs2crap/analytics/data/{item_category}/{item_prices_filename}.csv"
    )

    # Получаем коэффициент конвертации в рубли
    currency_mult = get_currency_mult()

    # Преобразуем цены в рубли
    df["price_rub"] = df["price"] / currency_mult

    # Вычисляем статистику для цен в рублях
    average_price_rub = df["price_rub"].mean()
    std_deviation_rub = df["price_rub"].std()
    max_price_rub = df["price_rub"].max()
    min_price_rub = df["price_rub"].min()

    # Выводим статистику для цен в рублях
    print("\n\nСредняя цена в рублях:", average_price_rub)
    print("Стандартное отклонение цен в рублях:", std_deviation_rub)
    print("Максимальная цена в рублях:", max_price_rub)
    print("Минимальная цена в рублях:", min_price_rub)

    # Установите N - количество последних дней для расчета среднего
    N = 30

    # Вычислите среднее значение цен за последние N дней
    average_price_last_N_days = df["price_rub"].tail(N).mean()
    print("\nСредняя цена за последние", N, "дней:", average_price_last_N_days)

    # Преобразование столбца с датой в тип datetime
    df["time"] = pd.to_datetime(df["time"], format="%b %d %Y %H")
    df.set_index("time", inplace=True)

    # Визуализация временного ряда
    plt.figure(figsize=(10, 6))
    plt.plot(df.index, df["price_rub"], label="Цена")
    plt.xlabel("Дата")
    plt.ylabel("Цена")
    plt.title("Временной ряд цен")
    plt.legend()
    plt.show()


# ==================================================================================================================================


if __name__ == "__main__":
    analysis("agents", "Crasswater The Forgotten Guerrilla Warfare")
