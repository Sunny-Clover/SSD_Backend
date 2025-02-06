from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List
from datetime import time, datetime
from .models import GenderEnum, StatusEnum
from enum import Enum


# 基底模型：用於共享欄位
class UserUpdatable(BaseModel):
    FirstName: Optional[str] = None
    LastName: Optional[str] = None
    Gender: Optional[GenderEnum] = None
    PhotoUrl: Optional[str] = None
    PostureAlertEnable: Optional[bool] = None
    PostureAlertTime: Optional[time] = None
    IdleAlertEnable: Optional[bool] = None
    IdleAlertTime: Optional[time] = None

class UserRegister(UserUpdatable):
    Email: EmailStr
    UserName: str
    Password: str

    @validator('Password')
    def password_length(cls, v):
        if len(v) < 8 or len(v) > 40:
            raise ValueError('Password must be between 8 and 40 characters')
        return v

class UserUpdate(UserUpdatable):
    pass

# 用於返回用戶資訊的模型
class UserResponse(UserUpdatable):
    UserID: int
    Email: Optional[EmailStr] = None
    UserName: str
    TotalPredictionCount: int
    TotalDetectionTime: time
    AllTimeScore: float

    class Config:
        from_attributes = True

class ExtendedUserResponse(UserResponse):
    # 前端需要的衍生欄位
    PR: float
    Level: int
    LevelProgress: float

class UserSearchResponse(BaseModel):
    UserID: int
    UserName: str
    PhotoUrl: str
    RequestState: Optional[str]
    IsFriend: bool

# 密碼更新模型
class PasswordUpdate(BaseModel):
    current_password: str
    new_password: str
    confirm_password: str

    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('New password and confirm password do not match')
        return v
    @validator('new_password')
    def password_length(cls, v):
        if not (8 <= len(v) <= 40):
            raise ValueError('Password must be between 8 and 40 characters')
        return v

# 好友請求相關模型
class FriendRequestCreate(BaseModel):
    ReceiverID: int

class FriendRequestSentResponse(BaseModel):
    RequestID: int
    ReceiverID: int
    ReceiverUserName: str
    Status: StatusEnum
    RequestDate: datetime

    class Config:
        from_attributes = True

class FriendRequestReceivedResponse(BaseModel):
    RequestID: int
    SenderID: int
    SenderUserName: str
    PhotoUrl: str
    RequestDate: datetime

    class Config:
        from_attributes = True

class FriendRequestResponse(BaseModel):
    RequestID: int
    SenderID: int
    SenderUserName: str
    ReceiverID: int
    ReceiverUserName: str
    Status: StatusEnum
    RequestDate: datetime

    class Config:
        from_attributes = True

class RequestAction(str, Enum):
    Accept = 'Accept'
    Reject = 'Decline'

class FriendRequestAction(BaseModel):
    Action: RequestAction  # 指定 


# 好友列表相關模型
class FriendListResponse(BaseModel):
    FriendID: int
    UserID1: int
    User1UserName: str
    UserID2: int
    User2UserName: str
    CreateDate: datetime
    ModDate: datetime

    class Config:
        from_attributes = True

class LeaderboardResponse(BaseModel):
    UserID: int
    UserName: str
    PhotoUrl: str
    Rank: int
    Level: int
    Progress: float
    AllTimeScore: float

# 認證相關模型
class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    refresh_token: str

class RefreshTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenPayload(BaseModel):
    sub: Optional[str] = None


# region: [schema] Bodypart create
class TorsoCreate(BaseModel):
    BackwardCount: int = 0
    ForwardCount: int = 0
    NeutralCount: int = 0
    AmbiguousCount: int = 0

    class Config:
        from_attributes = True

class FeetCreate(BaseModel):
    AnkleOnKneeCount: int = 0
    FlatCount: int = 0
    AmbiguousCount: int = 0

    class Config:
        from_attributes = True

class HeadCreate(BaseModel):
    BowedCount: int = 0
    NeutralCount: int = 0
    TiltBackCount: int = 0
    AmbiguousCount: int = 0

    class Config:
        from_attributes = True

class ShoulderCreate(BaseModel):
    HunchedCount: int = 0
    NeutralCount: int = 0
    ShrugCount: int = 0
    AmbiguousCount: int = 0

    class Config:
        from_attributes = True

class NeckCreate(BaseModel):
    ForwardCount: int = 0
    NeutralCount: int = 0
    AmbiguousCount: int = 0

    class Config:
        from_attributes = True
# endregion

# region: [schema] Bodypart response 
class TorsoResponse(TorsoCreate):
    PartialScore: float
class FeetResponse(FeetCreate):
    PartialScore: float
class HeadResponse(HeadCreate):
    PartialScore: float
class ShoulderResponse(ShoulderCreate):
    PartialScore: float
class NeckResponse(NeckCreate):
    PartialScore: float
# endregion


# Detection API 的請求和回應模型
class DetectionBase(BaseModel):
    StartTime: datetime
    EndTime: datetime
    TotalTime: time
    TotalPredictions: int    

class DetectionCreate(DetectionBase):
    Torso: TorsoCreate
    Feet: FeetCreate
    Head: HeadCreate
    Shoulder: ShoulderCreate
    Neck: NeckCreate


class DetectionResponse(DetectionBase):
    DetectionID: int
    UserID: int
    Score: float
    Torso: TorsoResponse
    Feet: FeetResponse
    Head: HeadResponse
    Shoulder: ShoulderResponse
    Neck: NeckResponse

    class Config:
        from_attributes = True


# 集合返回模型
class UsersPublic(BaseModel):
    data: List[UserResponse]
    count: int


class FriendRequestsPublic(BaseModel):
    data: List[FriendRequestResponse]
    count: int


class FriendListsPublic(BaseModel):
    data: List[FriendListResponse]
    count: int


class DetectionsPublic(BaseModel):
    data: List[DetectionResponse]
    count: int


# 通用成功訊息
class SuccessMessage(BaseModel):
    message: str
