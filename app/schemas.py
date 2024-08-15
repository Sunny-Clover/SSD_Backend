from pydantic import BaseModel, EmailStr

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
    FirstName: str | None = None
    LastName: str | None = None
    Gender: str | None = None
    PhotoUrl: str | None = None
    InstantPostureAlertEnable: bool = False
    PostureAlertDelayTime: str | None = None
    IdleAlertEnable: bool = False
    IdleAlertDelayTime: str | None = None
    AverageScore: float | None = None
    TotalTime: str | None = None

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