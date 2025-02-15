import sys
import site
sys.path.extend(site.getsitepackages())
from sqlmodel import SQLModel
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import DATABASE_URL
from app.core.security import decode_token
from app.api import auth, users, friends, friend_requests, blocked_list, detections
import uvicorn
import json

# 初始化 FastAPI 應用
app = FastAPI()
# 設定允許的來源，設定為前端的URL
origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,        # 允許的來源
    allow_credentials=True,
    allow_methods=["*"],          # 允許所有 HTTP 方法
    allow_headers=["*"],          # 允許所有標頭
)

# 用來儲存每位使用者的連線，格式：{username: {"phone": ws1, "viewer": ws2}}
connections = {}


print(DATABASE_URL)
# 資料庫設定(連線設定)
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 創建資料庫表格
SQLModel.metadata.create_all(bind=engine)

# 依賴注入的函數
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.websocket("/ws/{role}")  # role 為 "phone" 或 "viewer"
async def websocket_endpoint(websocket: WebSocket, role: str):
    token = websocket.query_params.get("token")

    payload = decode_token(token) if token else None
    if not payload:
        await websocket.close()
        return
    
    username = payload.get("sub")
    if not username:
        await websocket.close()
        return
        
    await websocket.accept()
    if username not in connections:
        connections[username] = {"phone": None, "viewer": None}
    connections[username][role] = websocket

    try:
        while True:
            message = await websocket.receive_text()
            # 僅轉發給相同 username 的另一端連線
            target = connections[username]["viewer"] if role == "phone" else connections[username]["phone"]
            if target:
                await target.send_text(message)
    except WebSocketDisconnect:
        connections[username][role] = None

app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(friends.router, prefix="/friends", tags=["friends"])
app.include_router(friend_requests.router, prefix="/friend-requests", tags=["friend_requests"])
app.include_router(blocked_list.router, prefix="/blocked-list", tags=["blocked_list"])
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(detections.router, prefix="/detections", tags=["detections"])

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)