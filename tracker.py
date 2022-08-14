import httpx
def get_tracking(client: httpx.Client, tracking_number: str):

    url = f"https://api.ship24.com/api/parcels/{tracking_number}?lang=en"

    json_payload = {
        "userAgent": "",
        "os": "Windows",
        "browser": "MS-Edge-Chromium",
        "device": "Unknown",
        "os_version": "windows-10",
        "browser_version": "104.0.1293.54",
        "uL": "en-CA",
    }

    headers = {
        "authority": "api.ship24.com",
        "accept": "application/json, text/plain, */*",
        "accept-language": "en-CA,en;q=0.9",
        "content-type": "application/json",
        "origin": "https://www.ship24.com",
        "referer": "https://www.ship24.com/",
        "sec-ch-ua": '"Chromium";v="104", " Not A;Brand";v="99", "Microsoft Edge";v="104"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.81 Safari/537.36 Edg/104.0.1293.54",
        "x-ship24-token": "225,150,128,44,49,54,54,48,53,48,51,56,56,51,57,54,49,44,225,150,130",
    }

    response = client.post(url=url, headers=headers, json=json_payload)

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
