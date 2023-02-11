import ast
import json
import random
from typing import List
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from fastapi.templating import Jinja2Templates

app = FastAPI()

templates = Jinja2Templates(directory="templates")

app.mount("/static", StaticFiles(directory="static"), name="static")

connections={}
random_list=[]
conn_with_ids = {}
async def ConnectionEstablish(data,rand=False):
    data [ 'your_id' ] = int(data [ 'your_id' ])
    data [ 'frnd_id' ] = int(data [ 'frnd_id' ])
    print(connections.keys())
    for i in connections.keys():
        print(set(i).issuperset({data['frnd_id']}),set(i).issuperset({data['your_id']}))
        if (set(i).issuperset({data['frnd_id']}) ^ set(i).issuperset({data['your_id']})):
            return await manager.send_msg_client({"type": "Connection", "status": "Already Connected With Others"}, data [ 'your_id' ])
    if data["frnd_id"] not in conn_with_ids:
        return await manager.send_msg_client({"type": "Connection", "status": "Refuse"}, data [ 'your_id' ])
    if tuple(sorted(( data [ 'your_id' ], data [ 'frnd_id' ] ))) in connections or rand:
        connections [ tuple(sorted(( data [ 'your_id' ], data [ 'frnd_id' ] ))) ] = True
        await manager.send_msg_client({"type": "Connection", "status": True,"frnd_id":data["frnd_id"]}, data [ 'your_id' ])
        await manager.send_msg_client({"type": "Connection", "status": True,"frnd_id":data["your_id"]}, data [ 'frnd_id' ])
    else:
        connections [ tuple(sorted(( data [ 'your_id' ], data [ 'frnd_id' ] )))] = False
    print(connections)
async def CollapseConnection(left_id):
    li=[0]
    for i in connections.keys():
        if set(i).issuperset({int(left_id)}):
            li=list(i)
            li.remove(int(left_id))
            connections.pop(i)
            break
    if li[0] in conn_with_ids:
        await manager.send_msg_client({"content":"Person Was Left From Chat","type":"CloseConn"},li[0])




class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = [ ]

    async def connect(self, websocket: WebSocket, ClientID):
        await websocket.accept()
        if ClientID in conn_with_ids:
            ClientID=random.choice([x for x in range(1,101) if x not in conn_with_ids])
        conn_with_ids [ ClientID ] = websocket
        self.active_connections.append(websocket)
        await websocket.send_json({"type":"uniqId","Id":ClientID})

    def disconnect(self, websocket: WebSocket, ClientID):
        conn_with_ids.pop(ClientID)
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message, websocket: WebSocket):
        await websocket.send_json(message)

    async def send_msg_client(self, message, ClientID):
        await conn_with_ids [ int(ClientID) ].send_json(message)
        '''for connection in self.active_connections:
            print('sasa',connection)
            await connection.send_text(message)'''
    async def boardcast_to_all(self,message):
        for connection in self.active_connections:
            await connection.send_json(message)


manager = ConnectionManager()


@app.get("/")
async def get(request: Request):
    return templates.TemplateResponse("UI.html", {"request": request})

'''@app.get("/ConnectWithId/{frnd_id}/{your_id}")
async def ConnectWithId(frnd_id:int, your_id:int):
    if sorted([your_id,frnd_id]) in connections:
        connections [ sorted([ your_id, frnd_id ]) ]=True
    else:
        connections[sorted([your_id,frnd_id])]=False'''

'''@app.get("/GetUniqueID/")
def getuniqueid():
    while True:
        UniqID=random.randrange(1,100)
        if UniqID in conn_with_ids:
            continue
        else:
            return {"type":'UniqueId',"Id":UniqID}'''

@app.websocket("/EstablishConn/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await manager.connect(websocket, client_id)
    await manager.boardcast_to_all({"type": "conncount", "status": len(conn_with_ids)})
    try:
        while True:
            print(conn_with_ids)
            data = await websocket.receive_text()
            data = ast.literal_eval(data)
            print(data)
            if data['type']=='FrndKey':
                await ConnectionEstablish(data)
            elif data["type"]=='RandConn':
                if random_list!=[]:
                    print(data['your_id'],random_list[0])
                    await ConnectionEstablish({"your_id": data [ 'your_id' ], "frnd_id": random_list [ 0 ]}, True)
                    random_list.pop()
                else:
                    random_list.append(data["your_id"])
            else:
                # await manager.send_personal_message(f"You wrote: {data['msg']", websocket)
                await manager.send_msg_client({"type":"msg","content":data['msg'],"name":data['name'],"img_no":data['img_no']}, data [ 'friend_id' ])
    except WebSocketDisconnect:
        manager.disconnect(websocket, client_id)
        await CollapseConnection(client_id)
        if client_id in random_list:
            random_list.remove(client_id)
        await manager.boardcast_to_all({"type": "conncount", "status": len(conn_with_ids)})
        #await manager.send_msg_client(f"Client #{client_id} left the chat", client_id)
    except:
        pass