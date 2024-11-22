from fastapi import FastAPI, Query
from datetime import timedelta
import requests
import json

app = FastAPI()

# In-memory cache for demonstration purposes
cache = {}

# Wind Direction
def WD(string):
    degree = int(string)
    if degree >= 0 and degree <= 89:
        return "North"
    elif degree >= 90 and degree <= 179:
        return "East"
    elif degree >= 180 and degree <= 269:
        return "South"
    else:
        return "West"

# Wind
def WDV(string):
    if len(string) == 6:
        degree = string[:2]
        speed = string[2:4]
        return f"wind is blowing from {degree} degrees (true) at a sustained speed of {speed} knots"
    elif len(string) == 7:
        degree = string[:3]
        speed = string[3:5]
        return f"wind is blowing from {degree} degrees (true) at a sustained speed of {speed} knots"
    elif len(string) == 9 and string[4] == "G":
        degree = string[:2]
        speed = string[2:4]
        gust = string[5:7]
        return f"wind is blowing from {degree} degrees (true) at a sustained speed of {speed} knots with {gust}-knot gusts."
    elif len(string) == 10 and string[5] == "G":
        degree = string[:3]
        speed = string[3:5]
        gust = string[6:8]
        return f"wind is blowing from {degree} degrees (true) at a sustained speed of {speed} knots with {gust}-knot gusts."

# Wind Variability
def WV(string):
    if (len(string) == 5 or len(string) == 6) and ord(string[2]) == 86:
        return f"wind direction varying between {string[:2]} and {string[3:]}"
    elif (len(string) == 6 or len(string) == 7) and ord(string[3]) == 86:
        return f"wind direction varying between {string[:3]} and {string[4:]}"

# Prevailing Visibility
def PV(string):
    if "SM" in string:
        res = string[:-2]
        return f"{res} statute mile"

# Temperature and Dewpoint
def TAD(string):
    if len(string) == 5 and ord(string[2]) == 47:
        return f"{string[:2]} is the temperature in degrees Celsius and {string[3:]} is the dewpoint in degrees Celsius."
    elif len(string) == 6 and ord(string[2]) == 47 and ord(string[3]) == 77:
        return f"{string[:2]} is the temperature in degrees Celsius and {string[3:]} is the dewpoint in Minus degrees Celsius."
    elif len(string) == 6 and ord(string[3]) == 47 and ord(string[0]) == 77:
        return f"{string[:3]} is the temperature in Minus degrees Celsius and {string[4:]} is the dewpoint in degrees Celsius."
    elif len(string) == 7 and ord(string[3]) == 47 and ord(string[0]) == 77 and ord(string[4]) == 77:
        return f"{string[:3]} is the temperature in Minus degrees Celsius and {string[4:]} is the dewpoint in Minus degrees Celsius."

# Cloud Layers
def Clouds(string):
    if string[:3] == "SKC":
        ans = "Sky Clear "
    elif string[:3] == "FEW":
        ans = "Few Sky Coverage "
    elif string[:3] == "SCT":
        ans = "Scattered Sky Coverage "
    elif string[:3] == "BKN":
        ans = "Broken "
    elif string[:3] == "OVC":
        ans = "Overcast "
    dig = int(string[3:])
    dig = str(dig) + "00"
    return ans + dig + " Feet AGL"

# Altimeter Setting
def AS(string):
    if ord(string[0]) == 65 and len(string) == 5:
        return f"current altimeter setting of {string[1:3]}.{string[3:]} inches Hg."
    if ord(string[0]) == 81 and len(string) == 5:
        return f"current altimeter setting of {string[1:]} hPa or {string[1:]} mb."

# Fetch Weather Information
def fetch_metar_data(station_code):
    metar_url = f"http://tgftp.nws.noaa.gov/data/observations/metar/stations/{station_code}.TXT"
    try:
        response = requests.get(metar_url)
        if response.status_code == 200:
            return response.text
    except Exception as e:
        print(f"Error fetching METAR data: {e}")
    return None

# Parse Weather Information
def parse_metar_data(metar_text):
    raw_data = {}
    raw_data['Data'] = {}
    data = metar_text.split()
    Udata = data[4:]
    raw_data['Data']['station'] = data[2]
    raw_data['Data']['last observation'] = data[0] + " at " + data[1] + " GMT"
    for i in data[3:]:
        if i in ["METAR", "SPECI"]:
            raw_data['Data']["Report Type"] = "Aviation Routine Weather Report" if i == "METAR" else "Special Report"
            Udata.remove(i)
        if "NOSIG" in i:
            raw_data['Data']['Remarks Overseas'] = "no significant changes"
            Udata.remove(i)
        if "KT" in i:
            raw_data['Data']['wind'] = WDV(i)
            Udata.remove(i)
        if "SM" in i:
            raw_data['Data']['prevailing_visibility'] = PV(i)
            Udata.remove(i)
        if ord(i[0]) == 65 and len(i) == 5 or ord(i[0]) == 81 and len(i) == 5:
            raw_data['Data']["altimeter setting"] = AS(i)
            Udata.remove(i)
        if len(i) == 5 and ord(i[2]) == 47:
            raw_data['Data']["Temperature and Dewpoint"] = TAD(i)
            Udata.remove(i)
        if i[:3] in ["SKC", "FEW", "SCT", "BKN", "OVC"]:
            if "Cloud Layers" not in raw_data['Data']:
                raw_data['Data']["Cloud Layers"] = []
            raw_data['Data']["Cloud Layers"].append(Clouds(i))
            Udata.remove(i)
    raw_data["Unprocessed Data"] = Udata
    return raw_data

# Get Weather Information (No Cache)
def get_weather_info(station_code):
    metar_data = fetch_metar_data(station_code)
    if metar_data:
        return parse_metar_data(metar_data)
    return None

# API Endpoints
@app.get("/metar/ping")
async def ping():
    return {"data": "pong"}

@app.get("/metar/raw")
async def get_weather_raw(scode: str = Query(..., description="Station Code (e.g., KSGS)")):
    weather_data = fetch_metar_data(scode)
    if weather_data:
        return {"Response": weather_data}
    return {"data": "Error fetching weather information"}

@app.get("/metar/processed")
async def get_weather_processed(scode: str = Query(..., description="Station Code (e.g., KSGS)")):
    weather_data = get_weather_info(scode)
    if weather_data:
        return {"Response": weather_data}
    return {"data": "Error fetching weather information"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
