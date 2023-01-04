import httpx


def setup_client(client: httpx.Client):
    url = "https://services.yuntrack.com/Track/Query"
    client.headers = {
        "Host": "services.yuntrack.com",
        "Accept-Language": "en-CA,en-US;q=0.8,en;q=0.5,zh-CN;q=0.3",
        "Content-Type": "application/json",
        "Authorization": "Nebula token:undefined",
        "Origin": "https://www.yuntrack.com",
        "Referer": "https://www.yuntrack.com/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
    }

    # a do-nothing request just to fetch cookies
    response = client.post(
        url=url,
        json={
            "NumberList": [""],
            "CaptchaVerification": "",
            "Year": 0,
        },
    )

    # update cookies
    client.cookies = response.cookies


def get_trackings(client: httpx.Client, *tracking_numbers: str):
    url = "https://services.yuntrack.com/Track/Query"

    json_payload = {
        "NumberList": [n for n in tracking_numbers],
        "CaptchaVerification": "",
        "Year": 0,
    }

    response = client.post(url=url, json=json_payload)
    if response.is_error:
        print("Error occured!!")
        print(response)
        print(response.text)
        return []

    parsed_info = []
    result_list = response.json()["ResultList"]

    for res in result_list:
        track_info = res["TrackInfo"]
        last_event = track_info["LastTrackEvent"]

        if "TrackCodeNameEx" in last_event.keys():
            TrackCodeName = "TrackCodeNameEx"
        else:
            TrackCodeName = "TrackCodeName"

        info = {"tracking_number": res["Id"]}
        info["last_event"] = {
            "process_date": last_event["ProcessDate"],
            "process_content": last_event["ProcessContent"],
            "process_location": last_event["ProcessLocation"],
            "status": last_event[TrackCodeName],
        }
        info["event_list"] = track_info["TrackEventDetails"]
        info["delivery_status"] = res["TrackData"]["TrackStatus"]

        parsed_info.append(info)

    return parsed_info


if __name__ == "__main__":
    with httpx.Client() as client:
        setup_client(client)
        # r = track_v2(client, "YT2221721272089274", "YT2221521272190130")
        # print(r)
        pass
