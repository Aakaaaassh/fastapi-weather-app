import streamlit as st
import requests
from bs4 import BeautifulSoup
import json

# Function to fetch station names dynamically
@st.cache_data
def fetch_station_names():
    url = "http://tgftp.nws.noaa.gov/data/observations/metar/stations/"  # Webpage URL
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        stations = []
        for link in soup.find_all("a"):
            href = link.get("href")
            if href and href.endswith(".TXT"):  # Ensure it's a station file
                station_name = href.split(".")[0]  # Extract name before '.TXT'
                stations.append(station_name)
        return sorted(stations)  # Return sorted station names
    else:
        st.error(f"Failed to fetch station names. Status code: {response.status_code}")
        return []

# Function to fetch weather data from the API
def fetch_data(api_url):
    try:
        response = requests.get(api_url)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error fetching data: {response.status_code}")
    except Exception as e:
        st.error(f"An error occurred: {e}")
    return None

# Streamlit App
def main():
    st.title("Weather Data Visualization")

    # Sidebar configuration
    st.sidebar.header("Configuration")
    api_url = "https://fastapi-weather-app.onrender.com/metar/processed"
    #api_url = st.sidebar.text_input("Enter API URL:", default_api_url)

    st.sidebar.write("Fetching station names...")
    stations = fetch_station_names()  # Fetch station names dynamically

    if stations:
        # Dropdown for station selection
        station_code = st.sidebar.selectbox("Select a Station Code:", options=stations)
    else:
        station_code = None
        st.sidebar.error("No station names available.")

    # Fetch and display data when the button is clicked
    if station_code and st.button("Fetch Weather Data"):
        full_url = f"{api_url}?scode={station_code}"
        data = fetch_data(full_url)
        if data and "Response" in data:
            response = data["Response"]
            st.subheader("Weather Details")

            # Display Station and Observation Details
            station = response["Data"].get("station", "N/A")
            observation = response["Data"].get("last observation", "N/A")
            st.markdown(f"**Station:** {station}")
            st.markdown(f"**Last Observation:** {observation}")

            # Display Wind Information
            wind = response["Data"].get("wind", "N/A")
            st.markdown(f"**Wind:** {wind}")

            # Display Visibility
            visibility = response["Data"].get("prevailing_visibility", "N/A")
            st.markdown(f"**Visibility:** {visibility}")

            # Display Cloud Layers
            cloud_layers = response["Data"].get("Cloud Layers", [])
            st.markdown("**Cloud Layers:**")
            st.write("\n".join([f"- {cloud}" for cloud in cloud_layers]) if cloud_layers else "No cloud data.")

            # Display Altimeter Setting
            altimeter = response["Data"].get("altimeter setting", "N/A")
            st.markdown(f"**Altimeter Setting:** {altimeter}")

if __name__ == "__main__":
    main()
