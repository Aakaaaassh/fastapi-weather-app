from fastapi import FastAPI, Query
from pydantic import BaseModel
import redis
from datetime import datetime, timedelta
import requests
import json


app = FastAPI()

# Initialize Redis connection
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)


#Wind Direction
def WD(string):

    """
    Converts a wind direction string to a cardinal direction.

    Args:
        string (str): The wind direction in degrees.

    Returns:
        str: The cardinal direction (e.g., 'North', 'East').
    """
    # Implementation details

    degree = int(string)
    if degree >= 0 and degree <= 89:
        return "North"
    elif degree >= 90 and degree <= 179:
        return "East"
    elif degree >= 180 and degree <= 269:
        return "South"
    else:
        return "West"

#Wind    
def WDV(string):

    """
    Parses wind speed and direction information.

    Args:
        string (str): Wind information string.

    Returns:
        str: Parsed wind information.
    """
    # Implementation details

    if len(string) == 6:
        degree = string[:2]
        speed = string[2:4]
        return "wind is blowing from " + str(degree) + " degrees (true) at a sustained speed of " + str(speed) + " knots"
    elif len(string) == 7:
        degree = string[:3]
        speed = string[3:5]
        return "wind is blowing from " + str(degree) + " degrees (true) at a sustained speed of " + str(speed) + " knots"
    elif len(string) == 9 and string[4] == "G":
        degree = string[:2]
        speed = string[2:4]
        gust = string[5:7]
        return "wind is blowing from " + str(degree) + " degrees (true) at a sustained speed of " + str(speed) + " knots  with " + str(gust) + "-knot gusts."
    elif len(string) == 10 and string[5] == "G":
        degree = string[:3]
        speed = string[3:5]
        gust = string[6:8]
        return "wind is blowing from " + str(degree) + " degrees (true) at a sustained speed of " + str(speed) + " knots  with " + str(gust) + "-knot gusts."
    elif len(string) == 10 and string[4] == "G":
        degree = string[:2]
        speed = string[2:4]
        gust = string[5:8]
        return "wind is blowing from " + str(degree) + " degrees (true) at a sustained speed of " + str(speed) + " knots  with " + str(gust) + "-knot gusts."
    elif len(string) == 11 and string[5] == "G":
        degree = string[:3]
        speed = string[3:5]
        gust = string[6:9]
        return "wind is blowing from " + str(degree) + " degrees (true) at a sustained speed of " + str(speed) + " knots  with " + str(gust) + "-knot gusts."


#Wind Variability
def WV(string):

    """
    Parses wind variability information.

    Args:
        string (str): Wind variability information string.

    Returns:
        str: Parsed wind variability information.
    """
    # Implementation details

    if (len(string) == 5 or len(string) == 6) and ord(string[2]) == 86:
        return "wind direction varying between " + string[:2] + " and " + string[3:]  
    elif (len(string) == 6 or len(string) == 7 ) and ord(string[3]) == 86:
        return "wind direction varying between " + string[:3] + " and " + string[4:]        

#Prevailing Visibility  
def PV(string):

    """
    Parses prevailing visibility information.

    Args:
        string (str): Prevailing visibility information string.

    Returns:
        str: Parsed prevailing visibility information.
    """
    # Implementation details


    if "SM" in string:
        res = string[:-2]
        return res + " statute mile"


#tempearture and Dewpoint
def TAD(string):

    """
    Parses temperature and dewpoint information.

    Args:
        string (str): Temperature and dewpoint information string.

    Returns:
        str: Parsed temperature and dewpoint information.
    """
    # Implementation details

    if (len(string) == 5 and ord(string[2]) == 47):
        return string[:2] + " is the temperature in degrees Celsius and " + string[3:] + " is the dewpoint in degrees Celsius."
    elif (len(string) == 6 and (ord(string[2]) == 47 and ord(string[3]) == 77)):
        return string[:2] + " is the temperature in degrees Celsius and " + string[3:] + " is the dewpoint in Minus degrees Celsius."
    elif (len(string) == 6 and (ord(string[3]) == 47 and ord(string[0]) == 77)):
        return string[:3] + " is the temperature in Minus degrees Celsius and " + string[4:] + " is the dewpoint in degrees Celsius."                     
    elif (len(string) == 7 and (ord(string[3]) == 47 and ord(string[0]) == 77 and ord(string[4]) == 77)):
        return string[:3] + " is the temperature in Minus degrees Celsius and " + string[4:] + " is the dewpoint in Minus degrees Celsius."

#Cloud Layers   
def Clouds(string):

    """
    Parses cloud layers information.

    Args:
        string (str): Cloud layers information string.

    Returns:
        str: Parsed cloud layers information.
    """
    # Implementation details

    if string[:3] == "SKC":
        ans = "Sky Clear "
    elif string[:3] == "FEW":
        ans = "Few Sky Coverage "
    elif string[:3] == "SCT":
        ans = "Scattered Sky Coverage "
    elif string[:3] == "BKN":
        ans = "Broken "
    elif string[:3] ==  "OVC":
        ans = "Overcast "
    dig = int(string[3:])
    dig = str(dig) + "00"
    return ans + dig + " Feet AGL" 


#Altimeter setting     
def AS(string):

    """
    Parses altimeter setting information.

    Args:
        string (str): Altimeter setting information string.

    Returns:
        str: Parsed altimeter setting information.
    """
    # Implementation details

    if ord(string[0]) == 65 and len(string) == 5:
        return "current altimeter setting of " + string[1:3] + "." + string[3:] + " inches Hg." 
    if ord(string[0]) == 81 and len(string) == 5:
        return "current altimeter setting of " + string[1:]+ " hPa or " + string[1:] + " mb."
    


#Get Weather Information
def get_weather_info(station_code, nocache):

    """
    Fetches and processes weather information.

    Args:
        station_code (str): The station code for weather data.
        nocache (bool): Set to True to bypass caching.

    Returns:
        dict: Processed weather information.
    """
    # Implementation details

    cached_data = redis_client.get(station_code)
    
    if not nocache and cached_data:
        return cached_data.decode('utf-8')
    
    metar_data = fetch_metar_data(station_code)
    
    if metar_data:
        # Parse METAR data here
        data =  parse_metar_data(metar_data)
        redis_client.setex(station_code, timedelta(minutes=5), json.dumps(data))
        return data
    return None

#Parse Weather Information
def parse_metar_data(metar_text):

    """
    Parses METAR weather data.

    Args:
        metar_text (str): Raw METAR weather data.

    Returns:
        dict: Parsed weather information.
    """
    # Implementation details

    raw_data = {}
    raw_data['Data'] = {}
    data = metar_text.split()
    Udata = data[4:]
    raw_data['Data']['station'] = data[2]  #station  
    raw_data['Data']['last observation'] = data[0] + " at " + data[1] + " GMT"  #last observation
    for i in data[3:]:
        if i in ["METAR","SPECI"]:
            if i == "METAR":
                raw_data['Data']["Report Type"] = "Aviation Routine Weather Report"             #Report Type
                Udata.remove(i)
            else:
                raw_data['Data']["Report Type"] = "Special Report"                               #Report Type
                Udata.remove(i)
        if "NOSIG" in i :
            raw_data['Data']['Remarks Overseas'] = "no significant changes"                    #Remarks Overseas
            Udata.remove(i)
        if "KT" in i:
            raw_data['Data']['wind'] = WDV(i)
            Udata.remove(i)
        if "AUTO" in i: 
            raw_data['Data']['observation type'] = "AUTO i.e Automatic"  #Observation Type
            Udata.remove(i)
        if "AO1" in i:
            raw_data['Data']['observation remark'] = i + " i.e CANNOT distinguish between rain and snow."  #Observation Remark
            Udata.remove(i)
        if "AO2" in i:
            raw_data['Data']['observation remark'] = i + " i.e CAN distinguish between rain and snow."       #Observation Remark
            Udata.remove(i)
        if "SM" in i:
            raw_data['Data']['prevailing_visibility'] = PV(i)
            Udata.remove(i)
        if (len(i) == 5 or len(i) == 6 or len(i) == 7) and (ord(i[2]) == 86 or ord(i[3]) == 86) :
            raw_data['Data']['Wind Variability'] = WV(i)
            Udata.remove(i)
        if (ord(i[0]) == 65 and len(i) == 5) or (ord(i[0]) == 81 and len(i) == 5):
            raw_data['Data']["altimeter setting"] = AS(i)
            Udata.remove(i)
        if (len(i) == 5 and ord(i[2]) == 47) or (len(i) == 6 and (ord(i[2]) == 47 and ord(i[3]) == 77))or(len(i) == 6 and (ord(i[3]) == 47 and ord(i[0]) == 77))or(len(i) == 7 and (ord(i[3]) == 47 and ord(i[0]) == 77 and ord(i[4]) == 77)):
            raw_data['Data']["Temperature and Dewpoint"] = TAD(i)
            Udata.remove(i)
        if i[:3] in ["SKC","FEW","SCT","BKN","OVC"]:
            if "Clouds Layers" not in raw_data['Data']:
                raw_data['Data']["Clouds Layers"] = []
                raw_data['Data']["Clouds Layers"].append(Clouds(i))
                Udata.remove(i)
            else:
                raw_data['Data']["Clouds Layers"].append(Clouds(i))
                Udata.remove(i)
        raw_data["Unprocessed Data"] = Udata
    return raw_data


#Fetch Weather Information
def fetch_metar_data(station_code):

    """
    Fetches raw METAR weather data from a source.

    Args:
        station_code (str): The station code for weather data.

    Returns:
        str: Raw METAR weather data.
    """
    # Implementation details

    # METAR data source URL for the station code
    metar_url = f'http://tgftp.nws.noaa.gov/data/observations/metar/stations/{station_code}.TXT'
    
    try:
        response = requests.get(metar_url)
        if response.status_code == 200:
            return response.text
    except Exception as e:
        print(f"Error fetching METAR data: {e}")
    
    return None


@app.get("/metar/ping")
async def ping():

    """
    Ping endpoint to check if the API is running.

    Returns:
        dict: Response indicating the API status.
    """
    # Implementation details

    return {"data": "pong"}

#Raw Data
@app.get("/metar/Raw info")
async def get_weather(
    scode: str = Query(..., description="Station Code (e.g., KSGS)")):

    """
    Endpoint to fetch raw METAR weather data.

    Args:
        scode (str): Station code.

    Returns:
        dict: Response containing raw METAR data.
    """
    # Implementation details

    
    weather_data = fetch_metar_data(scode)
    
    if weather_data:
        return { "Response": weather_data}
    else:
        return {"data": "Error fetching weather information"}




#Processessed Data
@app.get("/metar/Processed info")
async def get_weather(
    scode: str = Query(..., description="Station Code (e.g., KSGS)"),
    nocache: int = Query(1, description="Set to 1 to bypass cache")):

    """
    Endpoint to fetch and process weather information.

    Args:
        scode (str): Station code.
        nocache (int): Set to 1 to bypass caching.

    Returns:
        dict: Response containing processed weather information.
    """
    # Implementation details
    
    weather_data = get_weather_info(scode, nocache)
    
    if weather_data:
        return { "Response": weather_data}
    else:
        return {"data": "Error fetching weather information"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8080)
