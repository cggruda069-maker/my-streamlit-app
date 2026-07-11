import streamlit as st
import pandas as pd
import time
import random
import folium
from streamlit_folium import st_folium

# Page Configuration
st.set_page_config(page_title="Ola Ride Booking Simulator", page_icon="🚖", layout="wide")

st.title("🚖 Ola Ride Booking Dashboard")
st.caption("Streamlit me banaya gaya ek simple aur interactive ride booking system")

# --- Mock Data for Cities & Coordinates ---
CITIES = {
    "Delhi/NCR": {"lat": 28.6139, "lon": 77.2090},
    "Mumbai": {"lat": 19.0760, "lon": 72.8777},
    "Bengaluru": {"lat": 12.9716, "lon": 77.5946},
    "Kolkata": {"lat": 22.5726, "lon": 88.3639}
}

LOCATIONS = ["Connaught Place", "Airport Terminal 3", "Cyber City", "Noida Sector 62", 
             "Andheri West", "Bandra Kurla Complex", "Gateway of India", 
             "Indiranagar", "Whitefield", "Koramangala", "Salt Lake Sector V", "Park Street"]

# --- Sidebar Inputs ---
st.sidebar.header("📍 Ride Details")
selected_city = st.sidebar.selectbox("Apna City Chunein", list(CITIES.keys()))

# Filter locations based on simulation or just random pick for UI
pickup = st.sidebar.selectbox("Pickup Location", LOCATIONS, index=0)
drop = st.sidebar.selectbox("Drop Location", LOCATIONS, index=1)

if pickup == drop:
    st.sidebar.error("⚠️ Pickup aur Drop location same nahi ho sakte!")

# --- Session State Management ---
if "booking_status" not in st.session_state:
    st.session_state.booking_status = "Not Booked"
if "driver_name" not in st.session_state:
    st.session_state.driver_name = ""
if "otp" not in st.session_state:
    st.session_state.otp = ""

# --- Fare Calculation Logic ---
# Random distance generate kar rhe hain realistic feel ke liye
random.seed(len(pickup) + len(drop)) 
distance = round(random.uniform(5.0, 25.0), 2)

# Ride Options and Rates per km
ride_options = {
    "🚲 Ola Bike": {"base": 20, "per_km": 7, "time": "2 min away"},
    "🛺 Ola Auto": {"base": 30, "per_km": 11, "time": "3 min away"},
    "🚗 Ola Mini": {"base": 50, "per_km": 14, "time": "5 min away"},
    "🚙 Ola Prime Sedans": {"base": 70, "per_km": 18, "time": "4 min away"}
}

# --- Layout Layout Split ---
col1, col2 = st.columns([1, 1.2])

with col1:
    st.subheader("Available Rides")
    
    selected_ride = st.radio(
        "Kounsi gaadi book karni hai?",
        options=list(ride_options.keys()),
        format_func=lambda x: x
    )
    
    # Calculate Dynamic Price
    base_fare = ride_options[selected_ride]["base"]
    per_km_rate = ride_options[selected_ride]["per_km"]
    total_fare = base_fare + (distance * per_km_rate)
    
    # Fare breakdown card
    st.metric(label=f"Estimated Fare ({distance} km)", value=f"₹{round(total_fare, 2)}")
    st.info(f"⏱️ Driver Availability: {ride_options[selected_ride]['time']}")
    
    # --- Booking Actions ---
    if st.session_state.booking_status == "Not Booked":
        if st.button("Confirm & Book Ride 🚀", use_container_width=True, type="primary"):
            st.session_state.booking_status = "Searching"
            st.rerun()

    if st.session_state.booking_status == "Searching":
        with st.spinner("Nearby Drivers ko dhundha ja raha hai... Kripya thoda intezar karein..."):
            time.sleep(3) # Simulating driver match
            st.session_state.driver_name = random.choice(["Ramesh Kumar", "Suresh Yadav", "Amit Singh", "Satnam Singh"])
            st.session_state.otp = random.randint(1000, 9999)
            st.session_state.booking_status = "Confirmed"
            st.rerun()

    if st.session_state.booking_status == "Confirmed":
        st.success("🎉 Ride Book Ho Gayi Hai!")
        
        # Display Driver Info Table
        driver_data = {
            "Driver Partner": [st.session_state.driver_name],
            "Vehicle": [selected_ride.split(" ")[1]],
            "Rating": ["⭐ 4.8 / 5.0"],
            "STARTING OTP": [f"🔒 {st.session_state.otp}"]
        }
        st.table(pd.DataFrame(driver_data))
        
        if st.button("Cancel Ride ❌", use_container_width=True):
            st.session_state.booking_status = "Not Booked"
            st.rerun()

with col2:
    st.subheader("🗺️ Live Map View")
    
    # Map Center setup based on city
    center_lat = CITIES[selected_city]["lat"]
    center_lon = CITIES[selected_city]["lon"]
    
    # Folium Map integration
    m = folium.Map(location=[center_lat, center_lon], zoom_start=12, tiles="OpenStreetMap")
    
    # Dummy Coordinates for pickup/drop just to show on map visually
    folium.Marker(
        [center_lat + 0.01, center_lon + 0.01], 
        tooltip="Pickup", 
        popup=pickup, 
        icon=folium.Icon(color="green", icon="play")
    ).add_to(m)
    
    folium.Marker(
        [center_lat - 0.01, center_lon - 0.01], 
        tooltip="Drop", 
        popup=drop, 
        icon=folium.Icon(color="red", icon="stop")
    ).add_to(m)
    
    # Add dummy driver bots on map if searching or confirmed
    if st.session_state.booking_status in ["Searching", "Confirmed"]:
        folium.Marker(
            [center_lat + 0.005, center_lon - 0.002], 
            tooltip="Your Driver", 
            icon=folium.Icon(color="blue", icon="car", prefix="fa")
        ).add_to(m)

    # Render map in streamlit
    st_folium(m, width="100%", height=450)
