from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from app.models import User
from app.schemas import UserRegister, UserUpdate, UserResponse, PasswordUpdate, SuccessMessage
from app.core.security import get_password_hash, verify_password
from app.api.deps import CurrentUser, SessionDep

from typing import Annotated

router = APIRouter()

@router.post("/", response_model=UserResponse)
def create_user(user: UserRegister, db: SessionDep):
    # 檢查郵箱是否已經存在
    db_user = db.query(User).filter(User.Email == user.Email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="電子郵件已被註冊")
    
    # 檢查用戶名是否已經存在
    db_user = db.query(User).filter(User.UserName == user.UserName).first()
    if db_user:
        raise HTTPException(status_code=400, detail="用戶名已被使用")
    
    user_data = user.dict()
    user_data['Password'] = get_password_hash(user.Password)

    new_user = User(**user_data)

    # 添加並提交到資料庫
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user

@router.patch("/me", response_model=UserResponse)
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

    return db_user

@router.patch("/me/password", response_model=SuccessMessage)
def update_password(
    password_data: PasswordUpdate,
    current_user: CurrentUser,
    db: SessionDep
):
    # 1. 驗證當前密碼是否正確
    if not verify_password(password_data.current_password, current_user.Password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="當前密碼不正確",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 2. 確保新密碼與當前密碼不同
    if verify_password(password_data.new_password, current_user.Password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="新密碼不能與當前密碼相同",
        )
    
    hashed_new_password = get_password_hash(password_data.new_password)
    current_user.Password = hashed_new_password
    
    db.commit()
    db.refresh(current_user)
    
    return SuccessMessage(message="密碼更新成功")

@router.get("/me", response_model=UserResponse)
def read_users_me(current_user: CurrentUser):
    return current_user