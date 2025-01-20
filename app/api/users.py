from fastapi import APIRouter, Depends, HTTPException, status, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.models import User
from app.schemas import UserRegister, UserUpdate, UserResponse, PasswordUpdate, SuccessMessage, ExtendedUserResponse
from app.core.security import get_password_hash, verify_password
from app.api.deps import CurrentUser, SessionDep
from app.core.bll import calculate_user_level, calculate_user_level_progress, time_to_minutes
from pathlib import Path
import shutil

from typing import Annotated

router = APIRouter()

BASE_IMAGE_DIR = Path("app/images").resolve()
BASE_IMAGE_DIR.mkdir(parents=True, exist_ok=True)  # 確保目錄存在

@router.post("/", response_model=ExtendedUserResponse)
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

@router.patch("/me", response_model=ExtendedUserResponse)
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

    return get_userDTO(db, db_user)

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

@router.get("/me", response_model=ExtendedUserResponse)
def read_users_me(current_user: CurrentUser, db: SessionDep):
    return get_userDTO(db, current_user)

@router.post("/avatar")
def upload_photo(current_user: CurrentUser, file: UploadFile, db: SessionDep):
    # 檢查使用者是否存在
    db_user = db.query(User).filter(User.UserID == current_user.UserID).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="用戶未找到")

    # 檢查檔案類型
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Invalid file type, only images are allowed")

    # 提取副檔名
    file_extension = Path(file.filename).suffix
    if not file_extension:
        raise HTTPException(status_code=400, detail="File must have an extension")

    # 生成照片檔名
    photo_filename = f"avatar_{db_user.UserID}{file_extension}"
    photo_path = BASE_IMAGE_DIR / photo_filename

    # 儲存檔案
    with photo_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 更新使用者的照片檔名
    db_user.PhotoUrl = photo_filename
    db.commit()

    return {"message": "Photo uploaded successfully", "filename": photo_filename}

@router.get("/avatar/{user_id}")
def get_image(user_id: int, db: SessionDep):
    # 檢查使用者是否存在
    db_user = db.query(User).filter(User.UserID == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="用戶未找到")
    # 確保傳入的文件名安全
    try:
        sanitized_path = Path(db_user.PhotoUrl).name  # 僅保留檔名，移除路徑
        image_path = BASE_IMAGE_DIR / sanitized_path
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid image name")

    # 確保文件在指定的 BASE_IMAGE_DIR 內
    if not image_path.resolve().is_relative_to(BASE_IMAGE_DIR):
        raise HTTPException(status_code=400, detail="Invalid image path")

    # 檢查檔案是否存在
    if not image_path.exists() or not image_path.is_file():
        raise HTTPException(status_code=404, detail="Image not found")

    return FileResponse(image_path)

# region: depencies functions
def get_userDTO(db: Session, user: User) -> ExtendedUserResponse:
    user_dict = user.dict()

    pr = compute_user_percentile_rank(db, user)

    # Core transfer logic
    total_minutes = time_to_minutes(user.TotalDetectionTime)
    level = calculate_user_level(total_minutes)
    progress = calculate_user_level_progress(total_minutes, level)

    return ExtendedUserResponse(
        **user_dict,
        PR=pr,
        Level=level,
        LevelProgress=progress,
    )

def compute_user_percentile_rank(db: Session, user: User) -> float:
    user_score = user.AllTimeScore or 0.0

    # <= user_score
    count_lte = db.query(func.count(User.UserID)).filter(User.AllTimeScore <= user_score).scalar()
    # 全部人數
    count_all = db.query(func.count(User.UserID)).scalar()

    if not count_all:
        return 0.0
    
    pr = (count_lte / count_all) * 100
    return pr

# endregion