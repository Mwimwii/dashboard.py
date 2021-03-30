from typing import List
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm.session import Session
from starlette.requests import Request
from starlette.routing import request_response
from database import SessionLocal, engine
from datetime import datetime
import crud
import models
import schemas

# create the database
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# add middle ware classes
app.add_middleware(
    CORSMiddleware, # Enable Cross Origin Resource Sharing
    allow_origins=['127.0.0.1:8000',]
)

app.mount('/static', StaticFiles(directory='static'), name='static')

templates = Jinja2Templates(directory='templates')

# Dependancy returns a db connection and closses it once it's used
def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

# get current time and append to logs

# App startup events
@app.on_event('startup')
def startup_event():
    # init db, get db objs, do whatever
    with open('log.txt', mode='a') as log:
        time = datetime.now()
        msg: str = f'[{time}]: Application starting\n'
        # log.write(msg)

@app.on_event('shutdown')
def shutdown_event():
    # do shut down house cleaning
    with open('log.txt', mode='a') as log:
        time = datetime.now()
        msg: str = f'[{time}]: Application shutting down\n'
        log.write(msg)



class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str, websocket: WebSocket):
        for connection in self.active_connections:
            if connection is not websocket:
                await connection.send_json(message)

manager = ConnectionManager()


@app.get("/", response_class = HTMLResponse)
async def get(request: Request):
    return templates.TemplateResponse('home.html', {'request': request})


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int, db: Session = Depends(get_db)):
    await manager.connect(websocket)
    try:
        while True:
            sites = db.query(models.Website).all()
            # TODO: send models to websocket recipients
            data = await websocket.receive_text()
            # add site to db
            await manager.send_personal_message(f"You wrote: {data}", websocket)
            await manager.broadcast(f"Client #{client_id} says: {data}", websocket)
            #TODO: Figure out how to send objects to the users
            await manager.broadcast(sites, websocket)

    except WebSocketDisconnect as e:
        # TODO: log the exception
        print(f'Websocket error:\n{e}')
        with open('error.txt', mode='a') as log:
            time = datetime.now()
            msg: str = f'[{time}]: Websocket error:\n\t{e}\nApplication shutting down\n'
            log.write(msg)
        manager.disconnect(websocket)

        await manager.broadcast(f"Client #{client_id} left the chat")
    except Exception as e:
        with open('error.txt', mode='a') as log:
            time = datetime.now()
            msg: str = f'[{time}]: Websocket error:\n\t{e}\nApplication shutting down\n'
            log.write(msg)
        # TODO: Make a log here.

def ping_sites():
    pass