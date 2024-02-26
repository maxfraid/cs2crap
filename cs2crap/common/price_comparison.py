import pandas as pd
from typing import Optional

from cs2crap.common.utils import color_print

# ==================================================================================================================================
# |                                                          PRICE_COMPARISON                                                      |
# ==================================================================================================================================

"""
 ___________________________________________________________________________________________________________________________________________________
!                                                                                                                                                   |
!                                                                 NOTICE:                                                                           |
!                                                                                                                                                   |
!    Значения price_buy и price_sell не означают цену покупки и цену продажи.                                                                       |
!                                                                                                                                                   |
!    - price_buy: цена минимального выставленного лота определённого предмета на продажу (т. е. цена моментальной покупки при желании)              |
!    - price_sell: цена максимального выставленного запроса на автопокупку определённого предмета (т. е. цена моментальной продажи при желании)     |
!                                                                                                                                                   |
!    Путаница в названии переменных произошла намеренно: Манипулировать предметами хотелось моментально, соответсвенно продавать и покупать тоже.   |
!                                                                                                                                                   |
!___________________________________________________________________________________________________________________________________________________|

"""


def stm2stm_comparison(price_buy: float, price_sell: float) -> bool:
    """
    Сравнивает цены для перепродажи внутри рынка Steam.

    Parameters:
        - price_buy (float): Цена минимального выставленного на продажу лота в Steam.
        - price_sell (float): Цена максимального запроса на автопокупку в Steam.

    Returns:
        - bool: Результат сравнения. True, если разница между ценами превышает 20% от цены покупки
        \n\t(учитывая 13% комиссию с продажи - 7% выручка), в противном случае False.
    """

    if (float(price_buy) - float(price_sell)) > 0.2 * float(price_buy):
        return True
    else:
        return False


# ==================================================================================================================================


def csm2stm_comparison(
    item_hash_name: str, price_sell: float, price_buy: float
) -> Optional[tuple[int, bool, bool]]:
    """
    Сравнивает цены для перепродажи с CSGO Market в Steam.

    Parameters:
        - item_hash_name (str): Название предмета.
        - price_sell (float): Цена максимального запроса на автопокупку в Steam.
        - price_buy (float): Цена минимального выставленного на продажу лота в Steam.

    Returns:
        - Optional[tuple[int, bool, bool]]: Кортеж с результатом сравнения. Если предмет найден и цены успешно сравнены, возвращает кортеж вида
          (csgo_market_item_price, by_price_buy, by_price_sell), где:
            - csgo_market_item_price (int): Цена предмета на рынке CSGO Market.
            - by_price_buy (bool): Результат сравнения цены на CSGO Market с ценой автобая в Steam. True, если разница превышает 20%, в противном случае False.
            - by_price_sell (bool): Результат сравнения цены на CSGO Market с ценой минимального выставленного на продажу лота в Steam. True, если разница превышает 20%, в противном случае False.
        Если предмет не найден или произошла ошибка, возвращает None.
    """

    df = pd.read_csv("cs2crap/csgomarket/csgomarket_prices.csv")

    try:
        csgo_market_item_price = df.loc[
            df["market_hash_name"] == item_hash_name, "price"
        ].values[0]

        by_price_buy = (float(price_buy) - csgo_market_item_price) > 0.2 * float(
            price_buy
        )
        by_price_sell = (float(price_sell) - csgo_market_item_price) > 0.2 * float(
            price_sell
        )

        return int(csgo_market_item_price), by_price_buy, by_price_sell

    except Exception as e:
        color_print("fail", "fail", f"Ошибка сравнения цен маркетов: {e}", True)
        return None


# ==================================================================================================================================


def stm2csm_comparison(
    item_hash_name: str, price_sell: float, price_buy: float
) -> Optional[tuple[int, bool, bool]]:
    """
    Сравнивает цены для перепродажи с Steam на CSGO Market.

    Parameters:
        - item_hash_name (str): Название предмета.
        - price_sell (float): Цена максимального запроса на автопокупку в Steam.
        - price_buy (float): Цена минимального выставленного на продажу лота в Steam.

    Returns:
        - Optional[tuple[int, bool, bool]]: Кортеж с результатом сравнения. Если предмет найден и цены успешно сравнены, возвращает кортеж вида
          (csgo_market_item_price, by_price_buy, by_price_sell), где:
            - csgo_market_item_price (int): Цена предмета на рынке CSGO Market.
            - by_price_buy (bool): Результат сравнения цены автобая в Steam с ценой на CSGO Market. True, если разница превышает 20%, в противном случае False.
            - by_price_sell (bool): Результат сравнения цены минимального выставленного на продажу лота Steam с ценой на CSGO Market. True, если разница превышает 20%, в противном случае False.
        Если предмет не найден или произошла ошибка, возвращает None.
    """

    df = pd.read_csv("cs2crap/csgomarket/csgomarket_prices.csv")

    try:
        csgo_market_item_price = df.loc[
            df["market_hash_name"] == item_hash_name, "price"
        ].values[0]

        by_price_buy = (float(csgo_market_item_price) - float(price_buy)) > 0.2 * float(
            csgo_market_item_price
        )
        by_price_sell = (
            float(csgo_market_item_price) - float(price_sell)
        ) > 0.2 * float(csgo_market_item_price)

        return float(csgo_market_item_price), by_price_buy, by_price_sell

    except Exception as e:
        color_print("fail", "fail", f"Ошибка сравнения цен маркетов: {e}", True)
        return None
