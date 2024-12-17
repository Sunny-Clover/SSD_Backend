from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from app.models import User
from app.schemas import UserCreate, UserUpdate, UserResponse, PasswordUpdate, SuccessMessage
from app.core.security import get_password_hash
from app.api.deps import CurrentUser, SessionDep

from typing import Annotated

router = APIRouter()

@router.post("/", response_model=SuccessMessage)
def create_user(user: UserCreate, db: SessionDep):
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

    # TODO: 需改成回傳創建的使用者資訊
    return SuccessMessage(message="用戶註冊成功")

@router.patch("/me", response_model=SuccessMessage)
def update_user(user: UserUpdate, current_user: CurrentUser, db: SessionDep):
    db_user = db.query(User).filter(User.UserID == current_user.UserID).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="用戶未找到")
    
    update_data = user.dict(exclude_unset=True) # 保留有提供的欄位

    for field, value in update_data.items():
        if field == "Email" and value != db_user.Email:
            existing_user = db.query(User).filter(User.Email == user.Email).first()
            if existing_user:
                raise HTTPException(status_code=400, detail="電子郵件已被註冊")
        setattr(db_user, field, value)
    
    db.commit()
    db.refresh(db_user)
    print(f"db_user: {db_user.__dict__}") 
    
    return SuccessMessage(message="用戶資料更新成功")

@router.patch("/me/password", response_model=SuccessMessage)
def update_password(password_data: PasswordUpdate, current_user: CurrentUser, db: SessionDep):
    pass

@router.get("/me", response_model=UserResponse)
def read_users_me(current_user: CurrentUser):
    return current_user