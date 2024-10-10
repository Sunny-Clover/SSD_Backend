from pydantic import BaseModel, EmailStr
from typing import Optional

# for API 請求的請求體或回應的數據格式

class SuccessMessage(BaseModel):
    message: str

class UserCreate(BaseModel):
    Email: EmailStr
    UserName: str
    Password: str

class UserResponse(BaseModel):
    UserID: int
    UserName: str
    Email: EmailStr
    FirstName: Optional[str] = None
    LastName: Optional[str] = None
    Gender: Optional[str] = None
    PhotoUrl: Optional[str] = None
    InstantPostureAlertEnable: bool = False
    PostureAlertDelayTime: Optional[str] = None
    IdleAlertEnable: bool = False
    IdleAlertDelayTime: Optional[str] = None
    AverageScore: Optional[float] = None
    TotalTime: Optional[str] = None

    class Config:
        orm_mode = True

## 好友請求
class FriendRequestCreate(BaseModel):
    ReceiverID: int

class FriendRequestResponse(BaseModel):
    RequestID: int
    SenderID: int
    SenderUserName: str
    ReceiverID: int
    ReceiverUserName: str
    Status: str
    RequestDate: str

    class Config:
        orm_mode = True

class FriendRequestAction(BaseModel):
    Action: str  # 'accept' 或 'decline'

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class RefreshTokenRequest(BaseModel):
    refresh_token: str



# 部位紀錄的請求體或回應的數據格式
class BodyCreate(BaseModel):
    BackwardCount: int = 0
    ForwardCount: int = 0
    NeutralCount: int = 0
    class Config:
        orm_mode = True
        from_attributes = True

class FeetCreate(BaseModel):
    AnkleOnKneeCount: int = 0
    FlatCount: int = 0
    class Config:
        orm_mode = True
        from_attributes = True

class HeadCreate(BaseModel):
    BowedCount: int = 0
    NeutralCount: int = 0
    TiltBackCount: int = 0
    class Config:
        orm_mode = True
        from_attributes = True
        
class ShoulderCreate(BaseModel):
    HunchedCount: int = 0
    NeutralCount: int = 0
    ShrugCount: int = 0
    class Config:
        orm_mode = True
        from_attributes = True

class NeckCreate(BaseModel):
    ForwardCount: int = 0
    NeutralCount: int = 0
    class Config:
        orm_mode = True
        from_attributes = True

# Records api 的請求體或回應的數據格式
class RecordCreate(BaseModel):
    StartTime: str
    EndTime: str
    TotalTime: str
    TotalPredictions: int
    Body: BodyCreate
    Feet: FeetCreate
    Head: HeadCreate
    Shoulder: ShoulderCreate
    Neck: NeckCreate

class RecordResponse(BaseModel):
    RecordID: int
    UserID: int
    StartTime: str
    EndTime: str
    TotalTime: str
    TotalPredictions: int
    Body: BodyCreate  # 包含 Body 的資料
    Feet: FeetCreate  # 包含 Feet 的資料
    Head: HeadCreate  # 包含 Head 的資料
    Shoulder: ShoulderCreate  # 包含 Shoulder 的資料
    Neck: NeckCreate  # 包含 Neck 的資料

    class Config:
        orm_mode = True

