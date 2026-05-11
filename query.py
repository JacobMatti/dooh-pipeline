import sys
import boto3
import duckdb
from config import S3_BUCKET, AWS_REGION, PROCESSED_PREFIX

s3 = boto3.client("s3", region_name=AWS_REGION)

LOCAL_FILE = "dooh_scores.parquet"


def download_parquet():
    key = f"{PROCESSED_PREFIX}dooh_scores.parquet"
    s3.download_file(S3_BUCKET, key, LOCAL_FILE)


def query(title, sql):
    print(f"\n{title}")
    result = duckdb.query(sql).df()
    print(result.to_string(index=False))
    print()


def interactive():
    print("Interactive mode")
    while True:
        sql = input("query > ")
        if sql.strip():
            result = duckdb.query(sql).df()
            print(result.to_string(index=False))
            print()


if __name__ == "__main__":
    download_parquet()

    if len(sys.argv) > 1 and sys.argv[1] == "query":
        interactive()
    else:
        query("TOP 10 BEST OPPORTUNITIES OVERALL", f"""
            SELECT city, date, final_score, weather_condition, day_type
            FROM '{LOCAL_FILE}'
            ORDER BY final_score DESC
            LIMIT 10
        """)

        query("BEST CITY PER DAY", f"""
            SELECT date, city, final_score, weather_condition, day_type
            FROM '{LOCAL_FILE}'
            QUALIFY ROW_NUMBER() OVER (PARTITION BY date ORDER BY final_score DESC) = 1
            ORDER BY date
        """)

        query("TOP 10 WEEKENDS", f"""
            SELECT city, date, final_score, weather_condition
            FROM '{LOCAL_FILE}'
            WHERE day_type = 'weekend'
            ORDER BY final_score DESC
            LIMIT 10
        """)

        query("TOP 10 WEEKDAYS", f"""
            SELECT city, date, final_score, weather_condition
            FROM '{LOCAL_FILE}'
            WHERE day_type = 'weekday'
            ORDER BY final_score DESC
            LIMIT 10
        """)

        query("TOP 10 WORST DAYS", f"""
            SELECT city, date, final_score, weather_condition, day_type
            FROM '{LOCAL_FILE}'
            ORDER BY final_score ASC
            LIMIT 10
        """)

        query("CITY AVERAGES", f"""
            SELECT city,
                   ROUND(AVG(final_score), 2)   AS avg_final_score,
                   ROUND(AVG(event_score), 2)   AS avg_event_score,
                   ROUND(AVG(weather_score), 2) AS avg_weather_score,
                   ROUND(AVG(temp_score), 2)    AS avg_temp_score
            FROM '{LOCAL_FILE}'
            GROUP BY city
            ORDER BY avg_final_score DESC
        """)
