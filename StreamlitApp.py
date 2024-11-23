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
    st.title("METAR Code Translater")

    # Sidebar configuration
    st.sidebar.header("Configuration")
    api_url = "https://fastapi-weather-app.onrender.com/metar/processed"

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
            station = response["Data"].get("station code", "N/A")
            if station != "N/A":
                st.markdown(f"**Station:** {station}")

            observation = response["Data"].get("last observation", "N/A")
            if observation != "N/A":
                st.markdown(f"**Last Observation:** {observation}")

            current_day = response["Data"].get("current day", "N/A")
            if current_day != "N/A":
                st.markdown(f"**Day:** {current_day}")

            current_time = response["Data"].get("current time", "N/A")
            if current_time != "N/A":
                st.markdown(f"**Time:** {current_time}")

            # Display Wind Information
            wind = response["Data"].get("wind", "N/A")
            if wind != "N/A":
                st.markdown(f"**Wind:** {wind}")

            # Display Visibility
            visibility = response["Data"].get("prevailing visibility", "N/A")
            if visibility != "N/A":
                st.markdown(f"**Visibility:** {visibility}")

            # Temperature and Dewpoint
            Temp_dew = response["Data"].get("temperature and dewpoint", "N/A")
            if Temp_dew != "N/A":
                st.markdown(f"**Temperature & Dewpoint:** {Temp_dew}")

            # Display Cloud Layers
            cloud_layers = response["Data"].get("cloud layers", "N/A")
            if isinstance(cloud_layers, list) and cloud_layers:  # Check if it's a non-empty list
                st.markdown("**Cloud Layers:** ")
                st.write("\n".join([f"- {cloud}" for cloud in cloud_layers]))
            elif cloud_layers == "N/A":
                st.markdown("**Cloud Layers:** N/A")

            # Display Altimeter Setting
            altimeter = response["Data"].get("altimeter setting", "N/A")
            if altimeter != "N/A":
                st.markdown(f"**Altimeter Setting:** {altimeter}")

            # Sea Level
            sealevel = response["Data"].get("sea level", "N/A")
            if sealevel != "N/A":
                st.markdown(f"**Sea Level:** {sealevel}")

            # Observation Types
            ObservationTypeAuto = response['Data'].get('observation_type_AUTO', "N/A")
            if ObservationTypeAuto != "N/A":
                st.markdown(f"**Observation Type:** Automated Observation")
            
            ObservationTypeCorr = response['Data'].get('observation_type_COR','N/A')
            if ObservationTypeCorr != "N/A":
                st.markdown(f"**Observation Type:** Corrected Observation")
            
            # Observation
            Observation_AO1 = response["Data"].get("observation_AO1","N/A")
            if Observation_AO1 != "N/A":
                st.markdown(f"**AO1 Observation** {Observation_AO1}")
            
            Observation_AO2 = response["Data"].get("observation_AO2","N/A")
            if Observation_AO2 != "N/A":
                st.markdown(f"**AO2 Observation** {Observation_AO2}")

            Observation_AO2A = response["Data"].get("observation_AO2A","N/A")
            if Observation_AO2A != "N/A":
                st.markdown(f"**AO2A Observation** {Observation_AO2A}")

            


if __name__ == "__main__":
    main()
