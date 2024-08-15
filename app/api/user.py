from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models import User
from app.schemas import UserCreate, UserResponse, SuccessMessage
from app.core.database import SessionLocal, engine
from app.core.security import get_password_hash
from app.core.database import get_db
from app.dependencies import get_current_user
from typing import Annotated

router = APIRouter()

@router.post("/", response_model=SuccessMessage)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    # 檢查郵箱是否已經存在
    db_user = db.query(User).filter(User.Email == user.Email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="電子郵件已被註冊")
    
    # 檢查用戶名是否已經存在
    db_user = db.query(User).filter(User.UserName == user.UserName).first()
    if db_user:
        raise HTTPException(status_code=400, detail="用戶名已被使用")
    
    # 創建新用戶
    hashed_password = get_password_hash(user.Password)
    new_user = User(
        Email=user.Email,
        UserName=user.UserName,
        Password=hashed_password,
    )
    db.add(new_user)
    db.commit()

    return SuccessMessage(message="用戶註冊成功")


@router.get("/me", response_model=UserResponse)
def read_users_me(current_user: Annotated[UserResponse, Depends(get_current_user)]):
    return current_user