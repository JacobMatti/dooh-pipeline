import json
import boto3
import pandas as pd
from datetime import date
from config import (
    S3_BUCKET,
    AWS_REGION,
    WEATHER_PREFIX,
    EVENTS_PREFIX,
    PROCESSED_PREFIX,
    WEIGHTS,
    WEATHER_SCORES,
    TEMP_SCORES,
    DAY_SCORES,
)

s3 = boto3.client("s3", region_name=AWS_REGION)

SEGMENT_WEIGHTS = {
    "Sports":         4,
    "Music":          3,
    "Arts & Theatre": 2,
    "Family":         2,
    "Film":           2,
    "Miscellaneous":  1,
    "Undefined":      1,
}

WMO_CODE_MAP = {
    0:  "clearsky",
    1:  "clearsky",
    2:  "partlycloudy",
    3:  "cloudy",
    45: "fog",
    48: "fog",
    51: "rain",
    53: "rain",
    55: "rain",
    61: "rain",
    63: "rain",
    65: "rain",
    71: "snow",
    73: "snow",
    75: "snow",
    77: "snow",
    80: "rain",
    81: "rain",
    82: "rain",
    85: "snow",
    86: "snow",
    95: "thunderstorm",
    96: "thunderstorm",
    99: "thunderstorm",
}


def list_weather_files():
    response = s3.list_objects_v2(Bucket=S3_BUCKET, Prefix=WEATHER_PREFIX)
    return [obj["Key"] for obj in response.get("Contents", [])]


def parse_filename(key):
    filename = key.split("/")[-1].replace(".json", "")
    parts = filename.rsplit("_", 1)
    city_name = parts[0].replace("_", " ").title()
    day = date.fromisoformat(parts[1])
    return city_name, day


def read_from_s3(key):
    response = s3.get_object(Bucket=S3_BUCKET, Key=key)
    return json.loads(response["Body"].read())


def get_weather_score(weathercode):
    condition = WMO_CODE_MAP[weathercode]
    return WEATHER_SCORES[condition], condition


def get_temp_score(temp_f):
    if 65 <= temp_f <= 85:
        return TEMP_SCORES["ideal"], "ideal"
    elif 50 <= temp_f < 65:
        return TEMP_SCORES["good"], "good"
    elif 85 < temp_f <= 95:
        return TEMP_SCORES["neutral"], "neutral"
    elif temp_f < 40:
        return TEMP_SCORES["cold"], "cold"
    elif temp_f > 95:
        return TEMP_SCORES["hot"], "hot"
    elif 40 <= temp_f < 50:
        return TEMP_SCORES["cold"], "cold"


def get_event_score(events_data):
    events = events_data.get("_embedded", {}).get("events", [])

    unique_events = {}
    for event in events:
        name = event["name"]
        if name not in unique_events:
            segment = event.get("classifications", [{}])[0].get("segment", {}).get("name", "Undefined")
            unique_events[name] = segment

    raw_score = 0
    for name, segment in unique_events.items():
        raw_score += SEGMENT_WEIGHTS.get(segment, 0)

    event_score = round(min(raw_score / 10, 10), 2)
    event_names = ", ".join(unique_events.keys())
    return event_score, event_names


def get_day_score(day):
    if day.weekday() >= 5:
        return DAY_SCORES["weekend"], "weekend"
    return DAY_SCORES["weekday"], "weekday"


def get_final_score(event_score, weather_score, temp_score, day_score):
    return round(
        (event_score   * WEIGHTS["events"]) +
        (weather_score * WEIGHTS["weather"]) +
        (temp_score    * WEIGHTS["temp"]) +
        (day_score     * WEIGHTS["day"]),
        2
    )


if __name__ == "__main__":
    rows = []

    weather_files = list_weather_files()

    for weather_key in weather_files:
        city_name, day = parse_filename(weather_key)

        events_key = f"{EVENTS_PREFIX}{weather_key.split('/')[-1]}"

        weather_data = read_from_s3(weather_key)
        events_data  = read_from_s3(events_key)

        weathercode = weather_data["daily"]["weathercode"][0]
        temp_f      = weather_data["daily"]["temperature_2m_max"][0]

        weather_score, weather_condition = get_weather_score(weathercode)
        temp_score,    temp_category     = get_temp_score(temp_f)
        event_score,   event_names       = get_event_score(events_data)
        day_score,     day_type          = get_day_score(day)
        final_score                      = get_final_score(event_score, weather_score, temp_score, day_score)

        rows.append({
            "city":              city_name,
            "date":              day.isoformat(),
            "day_type":          day_type,
            "weather_condition": weather_condition,
            "temp_category":     temp_category,
            "events":            event_names,
            "event_score":       event_score,
            "weather_score":     weather_score,
            "temp_score":        temp_score,
            "day_score":         day_score,
            "final_score":       final_score,
        })

    scores_table = pd.DataFrame(rows)

    output_file = scores_table.to_parquet(index=False)
    s3.put_object(
        Bucket=S3_BUCKET,
        Key=f"{PROCESSED_PREFIX}dooh_scores.parquet",
        Body=output_file,
        ContentType="application/octet-stream",
    )
