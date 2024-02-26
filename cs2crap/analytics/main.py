import os

from cs2crap.analytics.data_manage import (
    get_category_data,
    get_items_category_count,
    get_items_list,
    get_items_price_history,
)
from cs2crap.common.utils import print_cscrap_logo


# ==================================================================================================================================
# |                                                     PRICES ANALYTICS MAIN FILE                                                 |
# ==================================================================================================================================


def get_history(items_category: str):
    """
    Создаёт файл со списком всех предметов в категории, получает историю цен для предметов.

    Parameters:
        - items_category (str): название категории предметов
    """

    category_data = get_category_data(items_category)
    request_url = category_data["request_url"]

    if not os.path.exists("cs2crap/analytics/data/" + items_category + ".csv"):
        if "items_count" not in category_data:
            get_items_category_count(items_category)
            category_data = get_category_data(items_category)

        request_count = (int(category_data["items_count"]) // 100) + 1
        get_items_list(items_category, request_url, 0, request_count * 100)

    get_items_price_history(items_category)


if __name__ == "__main__":
    print_cscrap_logo()
    get_history("containers")
