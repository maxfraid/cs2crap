import requests
import pandas as pd


# ==================================================================================================================================
# |                                                      CS:GO MARKET DATA_LOADER                                                  |
# ==================================================================================================================================


def get_csgomarket_items_prices(
    output_filename: str = "cs2crap/csgomarket/csgomarket_prices.csv",
) -> None:
    """
    Получает список всех предметов и их цены с сайта csgomarket.com, помещает их в указанный .csv файл.

    Parameters:
        - output_filename (str): название файла для вывода формата .csv
    """

    url = "https://market.csgo.com/api/v2/prices/RUB.json"

    output_csv = output_filename

    try:
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()

            items = data.get("items", [])

            df = pd.DataFrame(items)
            df = df[["market_hash_name", "price"]]

            df.to_csv(output_csv, index=False, encoding="utf-8")
        else:
            print(f"Ошибка при выполнении запроса: {response.status_code}")
    except Exception as e:
        print(f"Произошла ошибка: {e}")
