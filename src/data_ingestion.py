import os
import openmeteo_requests
import pandas as pd
import requests_cache
from retry_requests import retry

# 1. Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)

# 2. Define API parameters (Fixing the invalid longitude 768706 -> 76.8706)
url = "https://api.open-meteo.com/v1/forecast"
params = {
	"latitude": 8.5656,
	"longitude": 76.8706,
	"hourly": ["temperature_2m", "relative_humidity_2m", "dew_point_2m", "rain", "wind_speed_10m", "wind_direction_10m"],
	"timezone": "auto",
	"start_date": "2026-05-16",
	"end_date": "2026-05-21",
}
responses = openmeteo.weather_api(url, params = params)
response = responses[0]

# 3. Process hourly data
hourly = response.Hourly()
hourly_data = {
	"date": pd.date_range(
		start = pd.to_datetime(hourly.Time(), unit = "s", utc = True),
		end =  pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True),
		freq = pd.Timedelta(seconds = hourly.Interval()),
		inclusive = "left"
	).tz_convert(response.Timezone().decode())
}

hourly_data["temperature_2m"] = hourly.Variables(0).ValuesAsNumpy()
hourly_data["relative_humidity_2m"] = hourly.Variables(1).ValuesAsNumpy()
hourly_data["dew_point_2m"] = hourly.Variables(2).ValuesAsNumpy()
hourly_data["rain"] = hourly.Variables(3).ValuesAsNumpy()
hourly_data["wind_speed_10m"] = hourly.Variables(4).ValuesAsNumpy()
hourly_data["wind_direction_10m"] = hourly.Variables(5).ValuesAsNumpy()

# 4. Convert to DataFrame
hourly_dataframe = pd.DataFrame(data = hourly_data)

# Remove timezone offset metadata from strings so CSV handles it cleanly
hourly_dataframe['date'] = hourly_dataframe['date'].dt.strftime('%Y-%m-%d %H:%M:%S')

# 5. Create 'data' folder if it doesn't exist and save CSV
os.makedirs("data", exist_ok=True)
csv_path = os.path.join("data", "weather_data.csv")
hourly_dataframe.to_csv(csv_path, index=False)

print(f"Success! Data saved to {csv_path}")