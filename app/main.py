import sys
import site
sys.path.extend(site.getsitepackages())
from fastapi import FastAPI
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base
from app.config import DATABASE_URL
from app.api import auth, users, friends, friend_requests, blocked_list, records
import uvicorn

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


app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(friends.router, prefix="/friends", tags=["friends"])
app.include_router(friend_requests.router, prefix="/friend-requests", tags=["friend_requests"])
app.include_router(blocked_list.router, prefix="/blocked-list", tags=["blocked_list"])
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(records.router, prefix="/records", tags=["records"])

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)