import httpx


def get_tracking(client: httpx.Client, tracking_number: str):
    api_url = f"https://api.ship24.com/api/parcels/{tracking_number}"
    headers = {
        "origin": "https://www.ship24.com",
        "referer": "https://www.ship24.com/",
        "x-ship24-token": "225,150,128,44,49,54,54,48,51,57,55,51,51,55,51,53,51,44,225,150,130",
    }

    response = client.post(headers=headers, url=api_url, timeout=None)
    info = response.json()

    last_update_time = info["data"]["events"][0]["datetime"]

    events = [e["status"] for e in info["data"]["events"]]

    shipping_status = info["data"]["dispatch_code"]["desc"]

    return {
        "last_update_time": last_update_time,
        "events": events,
        "shipping_status": shipping_status,
    }


if __name__ == "__main__":
    with httpx.Client() as client:
        get_tracking(client, "YT2221521272091049")
        get_tracking(client, "YT2222421272086922")
