import os
from pathlib import Path

import httpx
import pandas as pd
import shopify
from dotenv import load_dotenv
from tqdm import tqdm

from tracker import get_trackings, setup_client

if __name__ == "__main__":
    load_dotenv()
    API_KEY = os.getenv("API_KEY")
    APP_PASSWORD = os.getenv("APP_PASSWORD")
    SHOP_NAME = os.getenv("SHOP_NAME")
    API_VERSION = "2022-07"

    shop_url = f"https://{API_KEY}:{APP_PASSWORD}@{SHOP_NAME}.myshopify.com/admin"

    with shopify.Session.temp(shop_url, API_VERSION, APP_PASSWORD):
        latest_order = 0
        all_orders = []

        # loop to get all orders
        while True:
            # get all the orders since `latest_order``
            query = shopify.Order.find(since_id=latest_order, limit=250)
            all_orders += query

            # set `latest_order` to the last order in the most recent query
            latest_order = all_orders[-1].id
            if len(query) < 250:
                break

    keys = ("created_at", "email", "fulfillments", "name")

    order_results = []
    tracking_nums = []
    tracking_num_to_order_index = {}

    for idx, o in tqdm(enumerate(all_orders)):
        order = {key: o.attributes[key] for key in keys}

        order["tracking_numbers"] = []  # list of tracking numbers
        order["tracking_urls"] = []  # list of links to tracking website

        order["last_update_time"] = []
        order["shipping_status"] = []
        order["last_event"] = []
        order["events"] = []

        if order["fulfillments"]:  # shipping information goes under fulfillments
            for fulfillment in order["fulfillments"]:
                for track_num in fulfillment.tracking_numbers:
                    order["tracking_numbers"].append(track_num)

                    tracking_nums.append(track_num)
                    tracking_num_to_order_index[track_num] = idx

                for track_url in fulfillment.tracking_urls:
                    order["tracking_urls"].append(track_url)

        del order["fulfillments"]  # don't need this in the final Excel sheet
        order_results.append(order)

    with httpx.Client() as client:
        setup_client(client)

        while tracking_nums:
            queued_trackings = []
            for _ in range(min(100, len(tracking_nums))):
                queued_trackings.append(tracking_nums.pop())

            parsed_trackings = get_trackings(client, *queued_trackings)
            for parsed_info in parsed_trackings:
                tracking_num = parsed_info["tracking_number"]
                index = tracking_num_to_order_index[tracking_num]

                last_event = parsed_info["last_event"]

                order_results[index]["last_update_time"].append(
                    last_event["process_date"])

                order_results[index]["shipping_status"].append(
                    parsed_info["delivery_status"])

                del parsed_info["last_event"]["process_date"]

                order_results[index]["last_event"] = tuple(
                    parsed_info["last_event"].values())

                order_results[index]["events"] += parsed_info["event_list"]

    Path("output").mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(order_results)
    df.to_excel("output/orders.xlsx")
