from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.models import User
from app.schemas import UserCreate, UserUpdate, UserResponse, SuccessMessage
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

    # 呼叫存儲過程注入假資料
    for year in range(2020, 2025, 1):
        db.execute(text("CALL InsertYearlyData(:p_year, :p_userID)"), {"p_year": year, "p_userID": new_user.UserID})
    db.commit()

    return SuccessMessage(message="用戶註冊成功")

'''
只更新有提供的欄位(不包含password)
'''
@router.put("/", response_model=SuccessMessage)
def update_user(user: UserUpdate, current_user: Annotated[UserResponse, Depends(get_current_user)], db: Session = Depends(get_db)):
    # 檢查用戶是否存在
    db_user = db.query(User).filter(User.UserID == current_user.UserID).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="用戶未找到")
    
    # 更新用戶資料
    update_data = user.dict(exclude_unset=True)  # 只保留提供的欄位
    for field, value in update_data.items():
        if field in ["Email"]:
            existing_user = db.query(User).filter(getattr(User, field) == value).first()
            if getattr(existing_user, "UserID") != current_user.UserID:
                raise HTTPException(status_code=400, detail=f"{field} 已被使用")
            
        setattr(db_user, field, value)  # 更新欄位

    db.commit()
    db.refresh(db_user)
    return SuccessMessage(message="用戶資料更新成功")

# 暫時先不用patch(partial update)
@router.patch("/", response_model=SuccessMessage)
def update_user(user: UserCreate, current_user: Annotated[UserResponse, Depends(get_current_user)], db: Session = Depends(get_db)):
    # 檢查用戶是否存在
    db_user = db.query(User).filter(User.UserID == current_user.UserID).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="用戶未找到")
    
    # 檢查郵箱是否已經存在
    if user.Email is not None and user.Email != db_user.Email:
        existing_user = db.query(User).filter(User.Email == user.Email).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="電子郵件已被註冊")
        db_user.Email = user.Email  # 更新郵箱
    
    # 檢查用戶名是否已經存在
    if user.UserName is not None and user.UserName != db_user.UserName:
        existing_user = db.query(User).filter(User.UserName == user.UserName).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="用戶名已被使用")
        db_user.UserName = user.UserName  # 更新用戶名
    
    # 更新密碼（如果提供了新密碼）
    if user.Password is not None:
        db_user.Password = get_password_hash(user.Password)  # 更新密碼
    
    db.commit()

    return SuccessMessage(message="用戶資料更新成功")

@router.get("/", response_model=UserResponse)
def read_users_me(current_user: Annotated[UserResponse, Depends(get_current_user)]):
    return current_user