import json


# ==================================================================================================================================
# |                                                       CS:GO MARKET UTILS                                                       |
# ==================================================================================================================================


def find_api_key(config_path: str = "cs2crap/csgomarket/config.json") -> str:
    """
    Достаёт из конфигурационного файла api-ключ для csgomarket

    Parameters:
        - config_path (str): путь к конфигурационному файлу, по умолчанию: "cs2crap/csgomarket/config.json".
    """

    with open(config_path, "r") as config_file:
        config_data = json.load(config_file)
        API_KEY = config_data.get("API_KEY")

    return API_KEY


# ==================================================================================================================================

if __name__ == "__main__":
    print(find_api_key())
