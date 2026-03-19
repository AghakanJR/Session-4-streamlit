import streamlit as st
import pandas as pd
import altair as alt

st.title("🚗 Car Sharing Performance Dashboard")

st.markdown("""
Welcome to the central hub for our car sharing operations. 
This interactive dashboard provides key insights into fleet performance, revenue generation, and user travel patterns. 

👈 **Use the sidebar to filter the data by car brand** and explore the metrics below.
---
""")

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

st.sidebar.title("Control Panel")
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
st.dataframe(trips_merged.head())

st.subheader("Trips Over Time")
trips_over_time = trips_merged.groupby("pickup_date").size()
st.line_chart(trips_over_time)

st.subheader("Revenue Per Car Model")
revenue_by_model_df = trips_merged.groupby("model")["revenue"].sum().reset_index()
st.bar_chart(data=revenue_by_model_df, x="model", y="revenue", color="model")
st.subheader("Cumulative Revenue Growth Over Time")
daily_revenue = trips_merged.groupby("pickup_date")["revenue"].sum()
cumulative_revenue = daily_revenue.cumsum()
st.area_chart(cumulative_revenue)

st.subheader("Bonus : Peak Hours (Trips by hour)")
trips_merged["pickup_hour"] = pd.to_datetime(trips_merged["pickup_time"]).dt.hour
trips_by_hour_df = trips_merged['pickup_hour'].value_counts().sort_index().reset_index()
trips_by_hour_df.columns = ['Hour', 'Trips']

peak_chart = alt.Chart(trips_by_hour_df).mark_bar().encode(
    x=alt.X('Hour:O', title='Hour of the Day'),
    y=alt.Y('Trips:Q', title='Number of Trips'),
    color=alt.Color('Trips:Q', scale=alt.Scale(scheme='greens'), legend=None)
)

st.altair_chart(peak_chart, use_container_width=True)