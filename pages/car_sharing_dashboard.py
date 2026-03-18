import streamlit as st
import pandas as pd

# Function to load CSV files into dataframes
@st.cache_data
def load_data():
    trips = pd.read_csv("data/trips.csv")
    cars = pd.read_csv("data/cars.csv")
    cities = pd.read_csv("data/cities.csv")
    
    return trips, cars, cities

# Merge trips with cars (joining on car_id)
trips_merged = trips.merge(cars, on="cars_id")

# Merge with cities for car's city (joining on city_id)
trips_merged = trips_merged.merge(cities, on="city_id")

trips_merged = trips_merged.drop(columns=["id_car", "city_id", "id_customer","id"])