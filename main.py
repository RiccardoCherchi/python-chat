import uvicorn

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.helpers.connection_manager import ConnectionManager
from app.db.config import client

app = FastAPI()

templates = Jinja2Templates(directory="app/templates")


@app.get("/", response_class=HTMLResponse)
async def read_item(request: Request):
    return templates.TemplateResponse("chat.j2", {"request": request})


@app.get('/users', response_class=HTMLResponse)
async def get_online_users(request: Request):
    users = [i.decode('UTF-8') for i in client.smembers("online_users")]
    return templates.TemplateResponse('users.j2', {"request": request, "users": users})


manager = ConnectionManager()


@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await manager.connect(websocket, user_id)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.send_personal_message(f"You wrote: {data}", websocket)
            await manager.broadcast(f"Client #{user_id} says: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)
        await manager.broadcast(f"Client #{user_id} left the chat")


if __name__ == "__main__":
    uvicorn.run("main:app", debug=True)
