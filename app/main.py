import sys
import site
sys.path.extend(site.getsitepackages())
from fastapi import FastAPI
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base
from app.config import DATABASE_URL
from app.api import auth

# 初始化 FastAPI 應用
app = FastAPI()

# 資料庫設定
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 創建資料庫表格
Base.metadata.create_all(bind=engine)

# 依賴注入的函數
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 載入 API 路由
from app.api import friends, friend_requests, blocked_list, user

app.include_router(user.router, prefix="/users", tags=["users"])
app.include_router(friends.router, prefix="/friends", tags=["friends"])
app.include_router(friend_requests.router, prefix="/friend-requests", tags=["friend_requests"])
app.include_router(blocked_list.router, prefix="/blocked-list", tags=["blocked_list"])
app.include_router(auth.router, prefix="/auth", tags=["auth"])
