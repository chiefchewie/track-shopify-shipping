from pprint import pprint
import sys

import httpx


def get_tracking(tracking_number: str):
    base_url = f"https://api.ship24.com/api/parcels/{tracking_number}"
    headers = {
        # "accept": "application/json, text/plain, */*",
        # "accept-encoding": "gzip, deflate, br",
        # "accept-language": "en-CA,en;q=0.9",
        # "content-type": "application/json",
        "origin": "https://www.ship24.com",
        "referer": "https://www.ship24.com/",
        # "sec-ch-ua": '"Chromium";v="104", " Not A;Brand";v="99", "Microsoft Edge";v="104"',
        # "sec-ch-ua-mobile": "?0",
        # "sec-ch-ua-platform": "Windows",
        # "sec-fetch-dest": "empty",
        # "sec-fetch-mode": "cors",
        # "sec-fetch-site": "same-site",
        # "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.81 Safari/537.36 Edg/104.0.1293.54",
        "x-ship24-token": "225,150,128,44,49,54,54,48,51,57,55,51,51,55,51,53,51,44,225,150,130",
    }
    try:
        response = httpx.post(headers=headers, url=base_url)
    except httpx.ReadTimeout as e:
        print(e)
        return

    info = response.json()

    last_update_time = info["data"]["events"][0]["datetime"]
    events = []
    for e in info["data"]["events"]:
        events.append(e["status"])
    shipping_status = info["data"]["dispatch_code"]["desc"]
    return {
        "last_update_time": last_update_time,
        "events": events,
        "shipping_status": shipping_status,
    }


# YT2221521272091049
# YT2222421272086922
get_tracking("YT2221521272091049")
