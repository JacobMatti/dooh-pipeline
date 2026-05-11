# DOOH Opportunity Pipeline

A data pipeline that scores 10 US cities across 10 days to identify the best opportunities for Digital Out-of-Home (DOOH) advertising. It pulls weather forecasts and live event data to produce a daily score for each city.

# How It Works

1. ingest.py — pulls weather (Open-Meteo) and events (Ticketmaster) data for the next 10 days and saves raw JSON to S3
2. transform.py — reads the raw files, scores each city/day, and saves a Parquet file to S3
3. query.py — downloads the Parquet file and runs SQL queries using DuckDB

# Scoring

Each city/day gets a final score out of 10 based on four factors:

| Factor | Weight |
---------------------
| Events | 35% |
| Weather | 25% |
| Temperature | 25% |
| Day of week | 15% |

Events are scored using Ticketmaster's segment classifications, Sports events score highest, down to Miscellaneous. Weather uses WMO codes from Open-Meteo mapped to scores from 0 (thunderstorm) to 10 (clear sky). Weekends score higher than weekdays.

# Output Columns

| Column | Description |
-------------------------
| city | City name |
| date | Date in YYYY-MM-DD format |
| day_type | weekend or weekday |
| weather_condition | clearsky, partlycloudy, cloudy, fog, rain, snow, or thunderstorm |
| temp_category | ideal, good, neutral, cold, or hot |
| events | Comma separated list of unique events happening that day |
| event_score | Event score out of 10 |
| weather_score | Weather score out of 10 |
| temp_score | Temperature score out of 10 |
| day_score | Day of week score (5 for weekday, 10 for weekend) |
| final_score | Weighted final score out of 10 |

# Setup

Add your Ticketmaster API key to config.py.


pip install boto3 requests pandas pyarrow duckdb
aws configure
aws s3 mb s3://dooh-pipeline


python ingest.py
python transform.py
python query.py
python query.py query  # interactive SQL mode

# S3 Structure

The S3 bucket is organized into two folders. The data folder contains raw weather and events JSON files per city per day. The processed folder contains the final scored Parquet file that gets queried.
