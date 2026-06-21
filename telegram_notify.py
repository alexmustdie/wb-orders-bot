import os
import requests

from collections import Counter
from datetime import datetime, timedelta

TELEGRAM_API_URL = "https://api.telegram.org/bot{token}/sendMessage"


def build_message(orders):
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%d-%m-%Y")
    total = len(orders)
    counter = Counter(order["article"] for order in orders)
    top3 = counter.most_common(3)
    lines = [f"Заказы за {yesterday}", f"Всего заказов: {total}", ""]
    if not top3:
        lines.append("Заказов за вчерашний день не было.")
    else:
        lines.append("Топ-3 артикула по количеству заказов:")
        for i, (article, count) in enumerate(top3, start=1):
            lines.append(f"{i}. {article} - {count} шт.")
    return "\n".join(lines)


def send_telegram_message(text, bot_token, chat_id):
    url = TELEGRAM_API_URL.format(token=bot_token)
    response = requests.post(url, data={"chat_id": chat_id, "text": text}, timeout=15)
    response.raise_for_status()
    return response.json()


def notify(orders):
    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if not bot_token or not chat_id:
        raise SystemExit("Не заданы TELEGRAM_BOT_TOKEN или TELEGRAM_CHAT_ID")
    message = build_message(orders)
    send_telegram_message(message, bot_token, chat_id)
    print("Сообщение отправлено в Telegram:\n" + message)
