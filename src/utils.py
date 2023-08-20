import random
from forex_python.converter import CurrencyRates
import logging


def get_header():
    """Gets a random user agent and returns it as a header.

    :return: A dictionary containing the header with a User-Agent
    :rtype: dict
    """
    agent_list = []

    # List of browsers (each browser has a text file with UA)
    browser_list = [
        "Firefox",
        "Internet+Explorer",
        "Opera",
        "Safari",
        "Chrome",
        "Edge",
        "Android+Webkit+Browser",
    ]

    # Randomly select which file browser to read
    browser = random.choice(browser_list)

    # File path
    file_path = f"../data/user_agents/{browser}.txt"

    with open(file_path, "r") as file:
        for line in file:
            if not line.startswith("More"):
                # Remove newline character and leading/trailing whitespace
                cleaned_line = line.strip()
                agent_list.append(cleaned_line)
    user_agent = random.choice(agent_list)
    header = {"User-Agent": user_agent}
    return header


def write_file(text, filename):
    """Writes to a text file
    :param text: text to be written to the file
    :param filename: name of the file"""
    with open(filename, "w") as f:
        f.write(text)


def read_file(filename):
    """Reads from a file
    :param filename: name of the file to be read
    :return: contents of the file
    :rtype: string"""
    with open(filename, "r") as f:
        file_content = f.read()
    return file_content


def formatPrice(price, currency):
    """Format price to add commas and currency symbol
    :param price: price to be formatted
    :return: formatted price
    """
    c = CurrencyRates()
    if currency == "EUR":
        return "€" + "{:,.0f}".format(price)
    elif currency == "PHP":
        return "₱" + "{:,.0f}".format(price)


# def convert_currency(df, new_currency):
#     c = CurrencyRates()
#     if new_currency == "EUR":
#         df["price"] = df["price"].apply(lambda x: c.convert("PHP", "EUR", x))
#     elif new_currency == "PHP":
#         df["price"] = df["price"].apply(lambda x: c.convert("EUR", "PHP", x))
#     return df


def add_eur_price(df):
    c = CurrencyRates()
    # get the conversion
    conversion = c.get_rate("PHP", "EUR")
    logging.info(f"Conversion rate: {conversion}")

    df["price_eur"] = df["price"] * conversion
    df["price_per_sqm_eur"] = df["price_per_sqm"] * conversion
    return df


def convert_to_eur(price):
    logging.info("Converting currency")
    c = CurrencyRates()
    return c.convert("PHP", "EUR", price)


def update_currency(sel_currency):
    if sel_currency == "PHP":
        currency = "PHP"
        price_col = "price"
        price_sqm = "price_per_sqm"
    else:
        currency = "EUR"
        price_col = "price_eur"
        price_sqm = "price_per_sqm_eur"

    return currency, price_col, price_sqm
