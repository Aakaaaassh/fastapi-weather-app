from fastapi import FastAPI, Query
from datetime import timedelta
import requests
import json

app = FastAPI()

# In-memory cache for demonstration purposes
cache = {}

# Day and Time
def Check_day_time(string):
    if len(string) == 7 and string[-1] == 'Z':
        Day = string[:2]
        Time = string[2:4] + ":" + string[4:6] + " UTC"
        return Day , Time
    else:
        return None

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
        Direction = WD(degree)
        return f"Wind is blowing from {Direction}, {degree} to be precise at a sustained speed of {speed} knots"
    elif len(string) == 7:
        degree = string[:3]
        speed = string[3:5]
        Direction = WD(degree)
        return f"Wind is blowing from {Direction}, {degree} to be precise at a sustained speed of {speed} knots"
    elif len(string) == 9 and string[4] == "G":
        degree = string[:2]
        speed = string[2:4]
        Direction = WD(degree)
        gust = string[5:7]
        return f"Wind is blowing from {Direction}, {degree} to be precise at a sustained speed of {speed} knots with {gust}-knot gusts."
    elif len(string) == 10 and string[5] == "G":
        degree = string[:3]
        speed = string[3:5]
        Direction = WD(degree)
        gust = string[6:8]
        return f"Wind is blowing from {Direction}, {degree} to be precise at a sustained speed of {speed} knots with {gust}-knot gusts."

# Wind Variability
def WV(string):
    if (len(string) == 5 or len(string) == 6) and ord(string[2]) == 86:
        return f"Wind direction varying between {string[:2]} and {string[3:]}"
    elif (len(string) == 6 or len(string) == 7) and ord(string[3]) == 86:
        return f"Wind direction varying between {string[:3]} and {string[4:]}"

# Prevailing Visibility
def PV(string):
    if "SM" in string:
        res = string[:-2]
        return f"Prevailing Visibility around {res} statute mile"

# Temperature and Dewpoint
def TAD(string):
    if len(string) == 5 and ord(string[2]) == 47:
        return f"Temperature is {string[:2]}° Celsius and the Dewpoint is {string[3:]}° Celsius."
    elif len(string) == 6 and ord(string[2]) == 47 and ord(string[3]) == 77:
        return f"Temperature is {string[:2]}° Celsius and the Dewpoint is -{string[4:]}° Celsius."
    elif len(string) == 6 and ord(string[3]) == 47 and ord(string[0]) == 77:
        return f"Temperature is -{string[1:3]}° Celsius and the Dewpoint is {string[4:]}° Celsius."
    elif len(string) == 7 and ord(string[3]) == 47 and ord(string[0]) == 77 and ord(string[4]) == 77:
        return f"Temperature is -{string[1:3]}° Celsius and the Dewpoint is -{string[5:]}° Celsius."

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
    dig = int(string[3:6])
    dig = str(dig) + "00"
    if string[6:8] == 'CB':
        return ans + dig + " Feet AGL" + 'with cloud type Cumulonimbus'
    elif string[6:9] == 'TCU':
        return ans + dig + " Feet AGL" + 'with cloud type Towering Cumulus'
    else:
        return ans + dig + " Feet AGL" 

# Altimeter Setting
def AS(string):
    if ord(string[0]) == 65 and len(string) == 5:
        return f"Current Altimeter Setting of {string[1:3]}.{string[3:]} inches Hg."
    if ord(string[0]) == 81 and len(string) == 5:
        return f"Current Altimeter Setting of {string[1:]} hPa or {string[1:]} mb."

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
    Day,Time = Check_day_time(data[3])
    Udata = data[4:]
    raw_data['Data']['station code'] = data[2]
    raw_data['Data']['current day'] = Day
    raw_data['Data']['current time'] = Time
    raw_data['Data']['last observation'] = data[0] + " at " + data[1] + " GMT"
    for i in data[3:]:
        if i in ["METAR", "SPECI"]:
            raw_data['Data']["report type"] = "Aviation Routine Weather Report" if i == "METAR" else "Special Report"
            Udata.remove(i)
        if "NOSIG" in i:
            raw_data['Data']['remarks overseas'] = "No significant changes"
            Udata.remove(i)
        if "KT" in i:
            raw_data['Data']['wind'] = WDV(i)
            Udata.remove(i)
        if "SM" in i:
            raw_data['Data']['prevailing visibility'] = PV(i)
            Udata.remove(i)
        if ord(i[0]) == 65 and len(i) == 5 or ord(i[0]) == 81 and len(i) == 5:
            raw_data['Data']["altimeter setting"] = AS(i)
            Udata.remove(i)
        if (len(i) == 5 and ord(i[2]) == 47) or (len(i) == 6 and ord(i[2]) == 47) or (len(i) == 6 and ord(i[3]) == 47) or (len(i) == 7 and ord(i[3]) == 47):
            raw_data['Data']["temperature and dewpoint"] = TAD(i)
            Udata.remove(i)
        if i[:3] in ["SKC", "FEW", "SCT", "BKN", "OVC"]:
            if "cloud layers" not in raw_data['Data']:
                raw_data['Data']["cloud layers"] = []
                cloud = []
            if i not in cloud:
                cloud.append(i)
                raw_data["Data"]["cloud layers"].append(Clouds(i))
                Udata.remove(i)
            
        if i == 'AUTO':
            raw_data['Data']['observation_type_AUTO'] = 'Automated observation'
            Udata.remove(i)
        if i == 'COR':
            raw_data['Data']['observation_type_COR'] = 'Corrected observation'
            Udata.remove(i)
        if i == 'AO1':
            raw_data['Data']['observation_AO1'] = 'Observation taken by equipment lacking a precipitation type discriminator (rain vs. snow)'
            Udata.remove(i)
        if i == 'AO2':
            raw_data['Data']['observation_AO2'] = 'Observation taken by standard equipment with a full complement of sensors'
            Udata.remove(i)
        if i == 'AO2A':
            raw_data['Data']['observation_AO2A'] = 'Automated observation augmented by a human observer'
            Udata.remove(i)
        if i == 'RMK':
            #raw_data["Data"]['remark'] = "Remark"
            Udata.remove(i)
        if len(i) == 6 and i[0:3] == 'SLP':
            if i[3] in ['5','6','7','8','9']:
                Dec = i[5]
                raw_data["Data"]['sea level'] = f"Current sea level pressure of 9{i[3:5]}.{Dec} millibars"
            elif i[3] in ['0','1','2','3','4']:
                Dec = i[5]
                raw_data["Data"]['sea level'] = f"Current sea level pressure of 10{i[3:5]}.{Dec} millibars"
            Udata.remove(i)
        if len(i) == 4:
            if ord(i[0]) in range(48,58) and ord(i[1]) in range(48,58) and ord(i[2]) in range(48,58) and ord(i[3]) in range(48,58):
                raw_data['Data']['prevailing visibility'] = f"Prevailing Visibility around {i} meters" 
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
@app.get("/")
async def root():
    return {"message": "Welcome to the METAR Code Translater App!"}

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
