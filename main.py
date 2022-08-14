import os
from pathlib import Path

import httpx
import pandas as pd
from dotenv import load_dotenv
from tqdm import tqdm

import shopify
from tracker import track_v2


def get_all_orders():
    latest_order = 0
    orders = []
    while True:
        query = shopify.Order.find(since_id=latest_order, limit=250)
        orders += query
        latest_order = orders[-1].id
        if len(query) < 250:
            break
    return orders


if __name__ == "__main__":
    load_dotenv()
    API_KEY = os.getenv("API_KEY")
    APP_PASSWORD = os.getenv("APP_PASSWORD")
    SHOP_NAME = os.getenv("SHOP_NAME")
    API_VERSION = "2022-07"

    shop_url = f"https://{API_KEY}:{APP_PASSWORD}@{SHOP_NAME}.myshopify.com/admin"

    with shopify.Session.temp(shop_url, API_VERSION, APP_PASSWORD):
        all_orders = get_all_orders()

    keys = ("created_at", "email", "fulfillments", "name")

    order_results = []
    all_tracking_numbers = []
    tracking_num_to_index = {}

    for i, o in tqdm(enumerate(all_orders)):
        order = {key: o.attributes[key] for key in keys}

        order["tracking_numbers"] = []
        order["tracking_urls"] = []

        order["last_update_time"] = []
        order["shipping_status"] = []
        order["last_event"] = []
        order["events"] = []

        if order["fulfillments"]:
            for fulfillment in order["fulfillments"]:
                for track_num in fulfillment.tracking_numbers:
                    order["tracking_numbers"].append(track_num)

                    all_tracking_numbers.append(track_num)
                    tracking_num_to_index[track_num] = i

                for track_url in fulfillment.tracking_urls:
                    order["tracking_urls"].append(track_url)

        del order["fulfillments"]  # don't need this in the final Excel sheet
        order_results.append(order)

    with httpx.Client() as client:
        while all_tracking_numbers:
            queued_trackings = []
            for _ in range(min(250, len(all_tracking_numbers))):
                queued_trackings.append(all_tracking_numbers.pop())

            parsed_trackings = track_v2(client, *queued_trackings)
            for pt in parsed_trackings:
                number = pt["tracking_number"]
                index = tracking_num_to_index[number]

                last_event = pt["last_event"]

                order_results[index]["last_update_time"].append(
                    last_event["process_date"])
                order_results[index]["shipping_status"].append(
                    pt["delivery_status"])
                order_results[index]["last_event"] = set(
                    pt["last_event"].values())
                order_results[index]["events"] += pt["event_list"]

    Path("output").mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(order_results)
    df.to_excel("output/orders.xlsx")
