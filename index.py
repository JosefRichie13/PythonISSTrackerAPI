from fastapi import FastAPI, Response, status, Request
import requests
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import threading
import time
from fastapi.templating import Jinja2Templates
from collections import deque
from datetime import datetime
from fastapi.staticfiles import StaticFiles




# Create a Deque [0,0,0,0,0,0,0,0,0,0] and length 10 to hold the coordinates.
# This holds only the latest 10 coordinates and is a FIFO queue
listOfCoordinates = deque([0] * 10, maxlen=10)



# Create a Lifespan event
# On the start of the App, a thread is created which calls the function, getCoordinates
@asynccontextmanager
async def lifespan(app: FastAPI):
    threading.Thread(target=getCoordinates, daemon=True).start()
    yield



# Initiate the App with Lifespan and templates
app = FastAPI(lifespan=lifespan)
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")



# Configures CORS settings
# Accepts CORS from any origin, method, headers
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



# Landing Page
@app.get("/")
def landingPage():
    return {"status": "Hello"}


# Function to convert Epoch to redable time
# Returns date in DD-MMM-YYYY HH:MM:SS format i.e. 11-Sept-2024 16:07:34 GMT
def epochToRedableTime(timeToConvert):
    convertedDate = datetime.fromtimestamp(timeToConvert)
    formatted_date = convertedDate.strftime("%d-%b-%Y %H:%M:%S")
    return str(formatted_date) + " IST"



# Function to generate ISS coordinates
def getCoordinates():

    # ISS URL which returns the coordinate details, this returns time in GMT
    issUrl = "http://api.open-notify.org/iss-now.json"

    # Another ISS URL, this returns time in browser time
    issUrlTwo = "https://api.wheretheiss.at/v1/satellites/25544"

    # Infinite loop, which requests the data from the URL
    # Parses and extracts all the details that are needed and appends to the dequeue
    # Sleeps for 60 seconds and loops again
    index = 0
    while index < 1:
        try:
            # Code if we are using the issUrl, this does not have Altitude or Speed data
            # requestData = requests.get(url=issUrl, timeout=50)
            # extractedData = requestData.json()
            # listOfCoordinates.appendleft({"latitude": extractedData["iss_position"]['latitude'], 
            #                                 "longitude": extractedData["iss_position"]['longitude'], 
            #                                 "timestamp": epochToRedableTime(extractedData["timestamp"])})
            
                        
            # Code if we are using the issUrlTwo, this has Altitude and Speed data
            requestData = requests.get(url=issUrlTwo, timeout=50)
            extractedData = requestData.json()
            listOfCoordinates.appendleft({"latitude": extractedData['latitude'], 
                                            "longitude": extractedData['longitude'], 
                                            "timestamp": epochToRedableTime(extractedData["timestamp"]),
                                            "altitude": (round(extractedData["altitude"], 2)),
                                            "velocity": (round(extractedData["velocity"], 2)),
                                            "sunLatitude": extractedData["solar_lat"],
                                            "sunLongitude": extractedData["solar_lon"]                                                                                     
                                            })

            print("Got response from API")
        except:
            print("API Failed to respond")

        time.sleep(60)



# Returns the coordinates as a list
@app.get("/getISSCoordinates")
def getISSCoordinates():
    return list(listOfCoordinates)



# Displays the map
@app.get("/showISSMap")
def showISSMap(request: Request):
    return templates.TemplateResponse(request=request, name="ISSVisual.html")
