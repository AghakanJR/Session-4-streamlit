import streamlit as st
import pandas as pd

# Function to load CSV files into dataframes
@st.cache_data
def load_data():
    trips = pd.read_csv("datasets/trips.csv")
    cars = pd.read_csv("datasets/cars.csv")
    cities = pd.read_csv("datasets/cities.csv")
    
    return trips, cars, cities

trips, cars, cities = load_data()

# Merge trips with cars (joining on car_id)
trips_merged = trips.merge(cars, left_on="car_id", right_on="id")

# Merge with cities for car's city (joining on city_id)
trips_merged = trips_merged.merge(cities, on="city_id")
trips_merged = trips_merged.drop(columns=["car_id", "city_id", "customer_id","id_x","id_y"])

trips_merged["pickup_date"] = pd.to_datetime(trips_merged["pickup_time"]).dt.date
trips_merged["dropoff_date"] = pd.to_datetime(trips_merged["dropoff_time"]).dt.date

cars_brand = st.sidebar.multiselect("Select the Car Brand", trips_merged["brand"].unique())
if cars_brand:
    trips_merged = trips_merged[trips_merged["brand"].isin(cars_brand)]

# Compute business performance metrics
total_trips = len(trips_merged) # Total number of trips
total_distance = trips_merged["distance"].sum() # Sum of all trip distances
# Car model with the highest revenue
top_car = trips_merged.groupby("model")["revenue"].sum().idxmax()
# Display metrics in columns
col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="Total Trips", value=total_trips)
with col2:
    st.metric(label="Top Car Model by Revenue", value=top_car)
with col3:
    st.metric(label="Total Distance (km)", value=f"{total_distance:,.2f}")

st.header("Visualizing the data")

st.subheader("Trips Over Time")
trips_over_time = trips_merged.groupby("pickup_date").size()
st.line_chart(trips_over_time)

st.subheader("Revenue Per Car Model")
revenue_by_model = trips_merged.groupby("model")["revenue"].sum()
st.bar_chart(revenue_by_model)

st.subheader("Cumulative Revenue Growth Over Time")
daily_revenue = trips_merged.groupby("pickup_date")["revenue"].sum()
cumulative_revenue = daily_revenue.cumsum()
st.area_chart(cumulative_revenue)

st.subheader("Bonus : Peak Hours (Trips by hour)")
trips_merged["pickup_hour"] = pd.to_datetime(trips_merged["pickup_time"]).dt.hour
trips_by_hour = trips_merged["pickup_hour"].value_counts().sort_index()
st.bar_chart(trips_by_hour)