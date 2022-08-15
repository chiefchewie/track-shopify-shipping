import httpx


def track_v2(client: httpx.Client, *tracking_numbers: str):
    url = "http://services.yuntrack.com/Track/Query"

    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-CA,en;q=0.9",
        "Authorization": "Nebula token:undefined",
        "Connection": "keep-alive",
        "Content-Type": "application/json",
        "Origin": "https://www.yuntrack.com",
        "Referer": "https://www.yuntrack.com/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.81 Safari/537.36 Edg/104.0.1293.54",
        "sec-ch-ua": '"Chromium";v="104", " Not A;Brand";v="99", "Microsoft Edge";v="104"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
    }

    json_payload = {
        "NumberList": [n for n in tracking_numbers],
        "CaptchaVerification": "",
        "Year": 0,
    }

    response = client.post(url=url, headers=headers, json=json_payload)
    if (response.is_error):
        print("Error occured!!")
        print(response)
        print(response.text)
        return []

    parsed_info = []
    result_list = response.json()["ResultList"]
    for res in result_list:

        track_info = res["TrackInfo"]
        last_event = track_info["LastTrackEvent"]

        info = {"tracking_number": res["Id"]}
        info["last_event"] = {
            "process_date": last_event["ProcessDate"],
            "process_content": last_event["ProcessContent"],
            "process_location": last_event["ProcessLocation"],
            "status": last_event["TrackCodeNameEx"],
        }
        info["event_list"] = track_info["TrackEventDetails"]
        info["delivery_status"] = res["TrackData"]["TrackStatus"]

        parsed_info.append(info)

    return parsed_info


if __name__ == "__main__":
    with httpx.Client() as client:
        r = track_v2(client, "YT2221521272091049", "YT2222421272086922")
        print(r)
