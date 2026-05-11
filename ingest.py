import json
import boto3
import requests
from datetime import date, timedelta
from config import (
    TICKETMASTER_API_KEY,
    S3_BUCKET,
    AWS_REGION,
    WEATHER_PREFIX,
    EVENTS_PREFIX,
    CITIES,
)

s3 = boto3.client("s3", region_name=AWS_REGION)

START_DATE = date.today() + timedelta(days=1)
END_DATE   = START_DATE + timedelta(days=10)

CITY_TIMEZONES = {
    "New York":    "America/New_York",
    "Los Angeles": "America/Los_Angeles",
    "Chicago":     "America/Chicago",
    "Houston":     "America/Chicago",
    "Phoenix":     "America/Phoenix",
    "Dallas":      "America/Chicago",
    "Miami":       "America/New_York",
    "Atlanta":     "America/New_York",
    "Seattle":     "America/Los_Angeles",
    "Denver":      "America/Denver",
}


def fetch_weather(city, day):
    url = "https://api.open-meteo.com/v1/forecast"
    day_str = day.isoformat()
    params = {
        "latitude":         city["lat"],
        "longitude":        city["lon"],
        "daily":            "temperature_2m_max,weathercode",
        "temperature_unit": "fahrenheit",
        "start_date":       day_str,
        "end_date":         day_str,
        "timezone":         CITY_TIMEZONES[city["name"]],
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()


def fetch_events(city, day):
    url = "https://app.ticketmaster.com/discovery/v2/events.json"
    day_str = day.isoformat()
    params = {
        "apikey":        TICKETMASTER_API_KEY,
        "city":          city["name"],
        "startDateTime": f"{day_str}T00:00:00Z",
        "endDateTime":   f"{day_str}T23:59:59Z",
        "size":          200,
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()


def save_to_s3(data, prefix, city_name, day):
    day_str = day.isoformat()
    key = f"{prefix}{city_name.lower().replace(' ', '_')}_{day_str}.json"
    s3.put_object(
        Bucket=S3_BUCKET,
        Key=key,
        Body=json.dumps(data),
        ContentType="application/json",
    )


if __name__ == "__main__":
    for city in CITIES:
        for i in range(10):
            day = START_DATE + timedelta(days=i)

            weather = fetch_weather(city, day)
            save_to_s3(weather, WEATHER_PREFIX, city["name"], day)

            events = fetch_events(city, day)
            save_to_s3(events, EVENTS_PREFIX, city["name"], day)
