from fastapi import FastAPI, Response, status, Request
import requests
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import threading
import time
from fastapi.templating import Jinja2Templates
from collections import deque
from datetime import datetime



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
# Returns 
def epochToRedableTime(timeToConvert):
    convertedDate = datetime.fromtimestamp(timeToConvert)
    formatted_date = convertedDate.strftime("%d-%b-%Y %H:%M:%S")
    return str(formatted_date) + " GMT"




# Function to generate ISS coordinates
def getCoordinates():

    # ISS URL which returns the coordinate details
    issUrl = "http://api.open-notify.org/iss-now.json"

    # Infinite loop, which requests the data from the URL
    # Parses and extracts the details (Latitude, Longitude, Timestamp) that are needed and appends to the dequeue
    # Sleeps for 60 seconds and loops again
    index = 0
    while index < 1:
        try:
            requestData = requests.get(url=issUrl, timeout=50)
            extractedData = requestData.json()
            listOfCoordinates.appendleft({"latitude": extractedData["iss_position"]['latitude'], 
                                            "longitude": extractedData["iss_position"]['longitude'], 
                                            "timestamp": epochToRedableTime(extractedData["timestamp"])})
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
