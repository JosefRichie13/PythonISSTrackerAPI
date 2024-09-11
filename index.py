from fastapi import FastAPI, Response, status, Request
import requests
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import threading
import time
from fastapi.templating import Jinja2Templates
from collections import deque 




listOfCoordinates = deque([0] * 10, maxlen=10)

@asynccontextmanager
async def lifespan(app: FastAPI):
    threading.Thread(target=getCoordinates, daemon=True).start()
    yield


app = FastAPI(lifespan=lifespan)
templates = Jinja2Templates(directory="templates")


origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def landingPage():
    return {"status": "Hello"}


def getCoordinates():
    issUrl = "http://api.open-notify.org/iss-now.json"
    index = 0

    while index < 1:
        try:
            requestData = requests.get(url=issUrl, timeout=50)
            print("Got response from API")
        except:
            print("API Failed to respond")
        extractedData = requestData.json()
        listOfCoordinates.appendleft({"latitude": extractedData["iss_position"]['latitude'], "longitude":extractedData["iss_position"]['longitude'], "timestamp": extractedData["timestamp"]})
        time.sleep(60)




@app.get("/getISSCoordinates")
def getISSCoordinates():
    return list(listOfCoordinates)





@app.get("/showISSMap")
def showISSMap(request:Request):
    return templates.TemplateResponse(request=request, name="ISSVisual.html")

