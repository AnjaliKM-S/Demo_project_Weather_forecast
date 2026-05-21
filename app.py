import streamlit as st
import pandas as pd
import os

st.set_page_config(
    page_title="Weather Forecast Dashboard",
    layout="wide"
)

st.title(" Weather Forecast Dashboard")

# CSV path
csv_path = os.path.join("data", "weather_data.csv")

# Check file exists
if os.path.exists(csv_path):

    # Load data
    data = pd.read_csv(csv_path)

    # Convert date column to datetime
    data["datetime"] = pd.to_datetime(data["date"])

    # Show dataframe
    st.subheader("Weather Data")
    st.dataframe(data)

    # Basic metrics
    st.subheader("Weather Summary")

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Average Temperature",
        f"{data['temperature_2m'].mean():.2f} °C"
    )

    col2.metric(
        "Total Rain",
        f"{data['rain'].sum():.2f} mm"
    )

    col3.metric(
        "Average Humidity",
        f"{data['relative_humidity_2m'].mean():.2f} %"
    )

    # Line chart
    st.subheader("Forecasted Rain Trend")

    st.line_chart(
        data,
        x="datetime",
        y="rain"
    )

else:
    st.error("CSV file not found! Please run data_ingestion.py first.")