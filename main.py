import os

from dotenv import load_dotenv

from fetch_orders import fetch_and_save
from telegram_notify import notify


if __name__ == "__main__":
    load_dotenv()
    wb_token = os.environ.get("WB_API_TOKEN")
    if not wb_token:
        raise SystemExit("Не задана переменная окружения WB_API_TOKEN")
    orders = fetch_and_save(wb_token, output_path="orders.csv")
    notify(orders)
