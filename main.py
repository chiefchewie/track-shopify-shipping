import os
from datetime import datetime

import pandas as pd
from dotenv import load_dotenv
from tqdm import tqdm

import shopify
from tracker import get_tracking


def get_all_orders():
    latest_order = 0
    orders = []
    while True:
        query = shopify.Order.find(since_id=latest_order, limit=30)
        orders += query
        latest_order = orders[-1].id
        if len(query) < 250:
            break
    return orders


if __name__ == "__main__":
    start_time = datetime.now()

    load_dotenv()
    API_KEY = os.getenv("API_KEY")
    APP_PASSWORD = os.getenv("APP_PASSWORD")
    SHOP_NAME = os.getenv("SHOP_NAME")
    API_VERSION = "2022-07"

    shop_url = f"https://{API_KEY}:{APP_PASSWORD}@{SHOP_NAME}.myshopify.com/admin"
    session = shopify.Session(shop_url, API_VERSION, APP_PASSWORD)

    shopify.ShopifyResource.activate_session(session)

    keys = (
        "created_at",
        "email",
        "fulfillments",
        "name",
    )

    order_results = []

    all_orders = get_all_orders()
    for o in tqdm(all_orders):
        order = {key: o.attributes[key] for key in keys}

        order["tracking_numbers"] = []
        order["tracking_urls"] = []
        order["last_update_time"] = []
        order["shipping_status"] = []
        order["events"] = []

        if order["fulfillments"]:
            for fulfillment in order["fulfillments"]:
                for track_num in fulfillment.tracking_numbers:
                    status = get_tracking(track_num)

                    order["tracking_numbers"].append(track_num)
                    order["last_update_time"].append(status["last_update_time"])
                    order["shipping_status"].append(status["shipping_status"])
                    order["events"] += status["events"]

                for track_url in fulfillment.tracking_urls:
                    order["tracking_urls"].append(track_url)

        order_results.append(order)

    df = pd.DataFrame(order_results)
    df.drop("fulfillments", axis=1, inplace=True)
    df.to_excel("orders.xlsx")

    shopify.ShopifyResource.clear_session()

    end_time = datetime.now()
    print("Duration: {}".format(end_time - start_time))
