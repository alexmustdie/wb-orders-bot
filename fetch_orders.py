import os
import csv
import requests

from datetime import datetime, timedelta

WB_ORDERS_URL = "https://statistics-api.wildberries.ru/api/v1/supplier/orders"


def get_yesterday_range():
    now = datetime.now()
    today_start = datetime(now.year, now.month, now.day)
    yesterday_start = today_start - timedelta(days=1)
    yesterday_end = today_start
    return yesterday_start, yesterday_end


def fetch_orders(token, date_from):
    headers = {"Authorization": token}
    params = {"dateFrom": date_from.strftime("%Y-%m-%dT%H:%M:%S")}
    response = requests.get(WB_ORDERS_URL, headers=headers, params=params, timeout=30)
    response.raise_for_status()
    return response.json()


def filter_by_order_date(orders, day_start, day_end):
    result = []
    for order in orders:
        order_dt = datetime.fromisoformat(order["date"])
        if day_start <= order_dt < day_end:
            result.append(order)
    return result


def map_order(order):
    order_dt = datetime.fromisoformat(order["date"])
    status = "Отменён" if order.get("isCancel") else "Новый"
    price = order.get("priceWithDisc", order.get("totalPrice", 0))
    return {
        "order_date": order_dt.strftime("%d-%m-%Y"),
        "article": order.get("supplierArticle", ""),
        "product_name": order.get("subject", ""),
        "status": status,
        "price": str(price).replace(".", ","),
    }


def save_to_csv(rows, filepath):
    fieldnames = ["order_date", "article", "product_name", "status", "price"]
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=";")
        writer.writeheader()
        writer.writerows(rows)


def fetch_and_save(token, output_path="orders.csv"):
    day_start, day_end = get_yesterday_range()
    raw_orders = fetch_orders(token, day_start)
    yesterday_orders = filter_by_order_date(raw_orders, day_start, day_end)
    mapped = [map_order(o) for o in yesterday_orders]
    save_to_csv(mapped, output_path)
    print(f"Сохранено {len(mapped)} заказов за {day_start.strftime('%d-%m-%Y')} -> {output_path}")
    return mapped
