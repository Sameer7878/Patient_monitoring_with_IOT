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
import Rasp_Sensor_Codes as rc
from multiprocessing import Process

app = FastAPI()

class User(BaseModel):
    username:str
    password:str
templates = Jinja2Templates(directory="templates")

app.mount("/static", StaticFiles(directory="static"), name="static")

active_tokens=[]
def Generate_Token():
    token=str(uuid4())
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

mx30 = rc.MAX30100()
mx30.enable_spo2()
#mx30.get_values()
flame=rc.Fire_detect(18,24)
acc=rc.Accelerometer()
#acc.detect()
oxy_pres=rc.Oxygen_Pressure(0x48)
saline_wg=rc.HX711()


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

def get_data_from_sensors(id):
    try:
        data = {
            1: {"data": {
                "patient_id":1,
                "pulse_oxi":mx30.get_values() ,
                "flame_check": flame.detect(),
                "motion_check": acc.detect(),
                "oxy_pres": oxy_pres.get_values(),
                "saline_per": saline_wg.get_values()
            }
            }

        }
    except Exception as e:
        print(e)
        
            
    return data[id]
token_with_websocket={}
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = [ ]

    async def connect(self, websocket: WebSocket, token):
        await websocket.accept()
        token_with_websocket[token]=websocket
        self.active_connections.append(websocket)
    def disconnect(self, websocket: WebSocket, token):
        print('disconn')
        token_with_websocket.pop(token)
        self.active_connections.remove(websocket)
    async def boardcast_to_web(self,data,token):
        await token_with_websocket[token].send_json(data)
        print('Done')

manager = ConnectionManager()

@app.get("/")
async def index(request : Request):
    return templates.TemplateResponse("dashboard/patient/index.html", {"request": request})

@app.get("/login/")
async def login(request:Request):
    return templates.TemplateResponse("login/index.html",{"request":request})

@app.get('/CheckSensor/{sensor_id}/')
def CheckSensor(sensor_id):
    sensor_list={1:{"state":True,"id":1},2:{"state":True,"id":2},3:{"state":True,"id":3},4:{"state":True,"id":4}}
    return sensor_list[int(sensor_id)]
@app.get("/SetInitialWG/{token}")
async def SetInitialWG(token):
    if token in active_tokens:
        return saline_wg.set_initial_weight()
@app.get("/GetHospitalData/{token}/")
async def GetHospitalData(token):
    print(token)
    print(active_tokens)
    if token in active_tokens:
        return {
        "type":"staff_data",
        "TotalCheckups":1,
        "TotalPatients":1,
        "TotalStaff":10,
        "ActiveBeds":1
        }
    return {"status":False}
@app.get("/GetRecentPatientData/{token}/")
async def GetPatientData(token):
    print(token)
    print(active_tokens)
    if token in active_tokens:
        return {1:{"patient_id":1,
                   "name":"sample",
                   "age":20,
                   "gender":"Male",
                   "mon_stat":False,
                   "assigned":None}

        }
    return {"status":False}
@app.get("/GetAllPatientData/{token}/")
async def GetPatientData(token):
    print(token)
    print(active_tokens)
    if token in active_tokens:
        return {1:{"id":1,
                   "name":"sample",
                   "age":20,
                   "gender":"Male",
                   "mon_stat":False,
                   "assigned":None}

        }
    return {"status":False}
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
'''@app.websocket("/EstablishConn/{token}")
async def websocket_endpoint(websocket: WebSocket,token:str):
    await manager.connect(websocket, token)
        #data = await websocket.receive_text()
    print(manager.active_connections)
    try:
        while True:
            time.sleep(10)
            print('hvghv')
            data = {
                1: {"data": {
                    "pulse_oxi": {"pulse": 80, "spo2": 150},
                    "flame_check": {"status": False},
                    "motion_check": {"status": False},
                    "oxy_pres": {"percentage": 50},
                    "saline_per": {"percentage": 90}
                }
                }

            }
            time.sleep(1)
            await manager.boardcast_to_all(data)
            data={
                1:{"data":{
                       "pulse_oxi":mx30.get_values(),
                       "flame_check":flame.detect(),
                       "motion_check":acc.detect(),
                       "oxy_pres":oxy_pres.get_values()
                   }
                }

            }
            await manager.boardcast_to_all(data)
    except WebSocketDisconnect:
        print('start')
        await manager.disconnect(websocket, token)
    while websocket:
        await websocket.send_json(mx30.get_values())
        await websocket.send_json(flame.detect())
        await websocket.send_json(acc.detect())
        await websocket.send_json(oxy_pres.get_values())'''
@app.websocket("/EstablishConn/{token}")
async def websocket_endpoint(websocket: WebSocket, token):
    await manager.connect(websocket, token)
    try:
        while True:
            input_data = await websocket.receive_text()
            print(input_data)
            # await manager.send_personal_message(f"You wrote: {data['msg']", websocket)
            await manager.boardcast_to_web(get_data_from_sensors(ast.literal_eval(input_data)['id']),token)
    except WebSocketDisconnect:
        manager.disconnect(websocket,token)
        #await manager.send_msg_client(f"Client #{client_id} left the chat", client_id)
    except:
        pass