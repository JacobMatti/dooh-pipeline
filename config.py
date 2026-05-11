TICKETMASTER_API_KEY = "e8GJ1cVwDC387BhuZQMmLQYe7TQ7cWnX"

S3_BUCKET = "dooh-pipeline"
AWS_REGION = "us-east-1"

WEATHER_PREFIX   = "data/weather/"
EVENTS_PREFIX    = "data/events/"
PROCESSED_PREFIX = "processed/"

CITIES = [
    {"name": "New York",    "lat": 40.71,  "lon": -74.01},
    {"name": "Los Angeles", "lat": 34.05,  "lon": -118.24},
    {"name": "Chicago",     "lat": 41.88,  "lon": -87.63},
    {"name": "Houston",     "lat": 29.76,  "lon": -95.37},
    {"name": "Phoenix",     "lat": 33.45,  "lon": -112.07},
    {"name": "Dallas",      "lat": 32.78,  "lon": -96.80},
    {"name": "Miami",       "lat": 25.76,  "lon": -80.19},
    {"name": "Atlanta",     "lat": 33.75,  "lon": -84.39},
    {"name": "Seattle",     "lat": 47.61,  "lon": -122.33},
    {"name": "Denver",      "lat": 39.74,  "lon": -104.99},
]

WEIGHTS = {
    "events":  0.35,
    "weather": 0.25,
    "temp":    0.25,
    "day":     0.15,
}

WEATHER_SCORES = {
    "clearsky":      10,
    "partlycloudy":   7,
    "cloudy":         5,
    "fog":            3,
    "rain":           2,
    "snow":           1,
    "thunderstorm":   0,
}

TEMP_SCORES = {
    "ideal":    10,
    "good":      7,
    "neutral":   5,
    "cold":      2,
    "hot":       2,
}

DAY_SCORES = {
    "weekday": 5,
    "weekend": 10,
}
