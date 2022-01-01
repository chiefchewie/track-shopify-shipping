import json
import os

import pandas as pd
import requests
import shopify
from dotenv import load_dotenv
from requests.models import HTTPError


def get_tracking(*args: str):
    """Returns the latest available shipping info from Aftership

    Args:
      args: one or more YunExpress tracking numbers

    Returns:
      a dictionary in the form {tracking_id: [last_update_time, checkpoint_msg, raw_location (if possible)]}

    Raises:
      HTTPError: If request to Aftership API failed
    """
    aftership_api = "https://track.aftership.com/api/v2/direct-trackings/batch"
    payload = {"direct_trackings": []}
    head = {
        "Host": "track.aftership.com",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:78.0) Gecko/20100101 Firefox/78.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-CA,en-US;q=0.7,en;q=0.3",
        "Accept-Encoding": "gzip, deflate, br",
        "Content-Type": "application/json",
        "b3": "69b0488be4bf54271e7384501c316882-2c9991fdcae410c8-0",
        "Content-Length": "97",
        "Origin": "https://track.aftership.com",
        "Connection": "keep-alive",
        "Cache-Control": "max-age=0",
        "TE": "Trailers"
    }
    for id in args:
        data = {
            "tracking_number": id,
            "additional_fields": {},
            "slug": "yunexpress"
        }
        payload["direct_trackings"].append(data)

    response = requests.post(url=aftership_api, json=payload, headers=head)
    if response.status_code != 201:
        raise HTTPError(
            f"Error for post request: ids={args}, response={response.status_code}")

    result_dict = json.loads(response.text)
    return_dict = {}
    for tracking in result_dict["data"]["direct_trackings"]:
        num = tracking["tracking_number"]
        if tracking["tracking"]["checkpoints"]:
            latest_msg = [
                tracking["tracking"]["checkpoints"][-1]["message"],
                tracking["tracking"]["checkpoints"][-1]["date_time"]
            ]
            if tracking["tracking"]["checkpoints"][-1]["address"]:
                latest_msg.append(
                    tracking["tracking"]["checkpoints"][-1]["address"]["raw_location"]
                )
        else:
            latest_msg = "N/A"
        return_dict[num] = latest_msg
    return return_dict


if __name__ == "__main__":
    load_dotenv()

    API_KEY = os.getenv("API_KEY")
    PASSWORD = os.getenv("API_SECRET")
    SHOP_NAME = os.getenv("SHOP_NAME")

    API_VERSION = "2021-10"
    SHOP_URL = f"https://{API_KEY}:{PASSWORD}@{SHOP_NAME}.myshopify.com/admin"

    # --BEGIN DOING THINGS--
    session = shopify.Session(SHOP_URL, API_VERSION, PASSWORD)
    shopify.ShopifyResource.activate_session(session)

    # keys to keep while reading orders
    useful_keys: list[str] = [
        "created_at",
        "customer",
        "email",
        "fulfillments",
        "fulfillment_status",
        "id",
        "name"
    ]

    # get all orders
    all_orders = shopify.Order.find(limit=250)

    # list of all parsed orders
    order_results = []

    # mapping of tracking num to index
    tracking_to_list_index: dict[str, int] = {}

    # set of all tracking numbers
    all_tracking_numbers = set()

    for i, order in enumerate(all_orders):

        # store useful attributes
        attrs = {k: order.attributes[k] for k in useful_keys}
        attrs["customer_name"] = order.attributes["billing_address"].attributes["name"]

        attrs["tracking_company"] = ""
        attrs["tracking_number"] = ""
        attrs["tracking_urls"] = ""
        attrs["shipping_status"] = ""

        # note - only works with one fulfillment and one tracking number
        if attrs["fulfillments"]:
            # TODO this returns an array - this code only deals with the first element
            current_fulfillment = attrs["fulfillments"][0]

            # get tracking company name
            attrs["tracking_company"] = current_fulfillment.attributes["tracking_company"]

            # TODO these return arrays but this only deals with the first one
            attrs["tracking_number"] = current_fulfillment.attributes["tracking_numbers"][0]
            attrs["tracking_urls"] = current_fulfillment.attributes["tracking_urls"][0]

            # store mappings - used to insert tracking information back into the indexed list
            tracking_to_list_index[attrs["tracking_number"]] = i

            all_tracking_numbers.add(attrs["tracking_number"])
        order_results.append(attrs)

    while all_tracking_numbers:
        # pop the top 50 or whats left into a list
        top50 = [all_tracking_numbers.pop()
                 for _ in range(min(50, len(all_tracking_numbers)))]

        # get tracking for these tracking numbers
        res = get_tracking(*top50)
        for tracking_num, status in res.items():
            # find the index of each tracking number
            # allowing us to insert the status message into the relevant field
            idx = tracking_to_list_index[tracking_num]
            order_results[idx]["shipping_status"] = status

    # convert list to dataframe
    df = pd.DataFrame(order_results)

    # column names - change as needed
    cols = ['name', 'created_at', 'customer_name', 'email',  'tracking_company',
            'tracking_number', 'tracking_urls', 'shipping_status']
    df = df[cols]

    # output directory - where to store the Excel file
    directory = "./output"
    if not os.path.exists(directory):
        os.makedirs(directory)

    df.to_excel(f"output/orders.xlsx")

    # --FINISH DOING THINGS--
    shopify.ShopifyResource.clear_session()
