import ast
import json
import random
from typing import List
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from pydantic import BaseModel
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from fastapi.templating import Jinja2Templates
from uuid import uuid4
import time
#import Rasp_Sensor_Codes as rc
from multiprocessing import Process

app = FastAPI()

class User(BaseModel):
    username:str
    password:str
templates = Jinja2Templates(directory="templates")

app.mount("/static", StaticFiles(directory="static"), name="static")

active_tokens=[]
def Generate_Token():
    token=uuid4()
    if token not in active_tokens:
        active_tokens.append(token)
        return token
    return Generate_Token()

def runInParallel(*fns):
  proc = []
  for fn in fns:
    p = Process(target=fn)
    p.start()
    proc.append(p)
  for p in proc:
    p.join()

'''mx30 = rc.MAX30100()
mx30.enable_spo2()
#mx30.get_values()
flame=rc.Fire_detect(18,24)
acc=rc.Accelerometer()
#acc.detect()
oxy_pres=rc.Oxygen_Pressure(0x48)'''

html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>WebSocket Chat</h1>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
            var ws = new WebSocket("ws://localhost:8000/ws");
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)
            };
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                ws.send(input.value)
                input.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""

token_with_websocket={}
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = [ ]

    async def connect(self, websocket: WebSocket, token):
        await websocket.accept()
        token_with_websocket[token]=websocket
        self.active_connections.append(websocket)
        if websocket in self.active_connections:
            await websocket.send_json({"status":True,"token":token})
        else:
            await websocket.send_json({"status": False, "token": token})

    def disconnect(self, websocket: WebSocket, token):
        token_with_websocket.pop(token)
        self.active_connections.remove(websocket)
    async def boardcast_to_all(self,data):
        for connection in self.active_connections:
            await connection.send_json(data)

manager = ConnectionManager()

@app.get("/")
async def index(request : Request):
    return templates.TemplateResponse("dashboard/patient/index.html", {"request": request})

@app.get("/login/")
async def login(request:Request):
    return templates.TemplateResponse("login/index.html",{"request":request})

@app.post("/VerifyLogin/")
def verify_login(user:User):
    if user.username=="admin" and user.password=="admin":
        token=Generate_Token()
        return {"status":True,"token":token}
    return {"status":False,"token":None}
@app.get("/GetCurrentOxygenPressure/")
def get_oxy_pres():
    return None#oxy_pres.get_values()
@app.get("/GetPulseSpo2/")
def get_pul_spo2():
    return None #mx30.get_values()
@app.get("/GetAcceleromterStatus/")
def get_motion():
    return None# acc.detect()
@app.get("/GetFlameAlert/")
def get_flame_det():
    return None# flame.detect()
@app.websocket("/EstablishConn/{token}")
async def websocket_endpoint(websocket: WebSocket,token):
    await manager.connect(websocket, token)
        #data = await websocket.receive_text()
    try:
        while True:
            data={

            }
    except:
        pass
    '''while websocket:
        await websocket.send_json(mx30.get_values())
        await websocket.send_json(flame.detect())
        await websocket.send_json(acc.detect())
        await websocket.send_json(oxy_pres.get_values())'''