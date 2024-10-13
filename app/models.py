from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import UniqueConstraint, ForeignKeyConstraint
from typing import Optional
from datetime import time, datetime
from enum import Enum
import uuid


# 定義性別選項
class GenderEnum(str, Enum):
    Male = "Male"
    Female = "Female"
    Other = "Other"

class StatusEnum(str, Enum):
    Pending = "Pending"
    Accepted = "Accepted"
    Declined = "Declined"

# 基底類別：包含時間戳的共用欄位
class TimestampMixin(SQLModel):
    CreateDate: Optional[datetime] = Field(default_factory=datetime.utcnow)
    ModDate: Optional[datetime] = Field(default_factory=datetime.utcnow, sa_column_kwargs={"onupdate": datetime.utcnow})

# User 表
class UserBase(SQLModel):
    UserName: str = Field(max_length=50, nullable=False, unique=True)
    Email: str = Field(max_length=100, nullable=False, unique=True)
    FirstName: Optional[str] = Field(default='', max_length=50)
    LastName: Optional[str] = Field(default='', max_length=50)
    Gender: Optional[GenderEnum] = Field(default="Other")
    PhotoUrl: Optional[str] = Field(default='', max_length=255)
    PostureAlertEnable: Optional[bool] = Field(default=False)
    PostureAlertTime: Optional[time] = Field(default='00:00:00')
    IdleAlertEnable: Optional[bool] = Field(default=False)
    IdleAlertTime: Optional[time] = Field(default='00:00:00')
    AllTimeScore: Optional[float] = Field(default=0.0)
    TotalDetectionTime: Optional[time] = Field(default='00:00:00')

class User(UserBase, TimestampMixin, table=True):
    UserID: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    Password: str = Field(max_length=255, nullable=False)


# FriendList 表
class FriendList(TimestampMixin, table=True):
    FriendID: Optional[int] = Field(default=None, primary_key=True)
    UserID1: uuid.UUID = Field(nullable=False)
    UserID2: uuid.UUID = Field(nullable=False)

    __table_args__ = (
        UniqueConstraint("UserID1", "UserID2"),  # 使用 UniqueConstraint 來定義組合唯一約束
        ForeignKeyConstraint(["UserID1"], ["user.UserID"], name="fk_friendlist_user1"),
        ForeignKeyConstraint(["UserID2"], ["user.UserID"], name="fk_friendlist_user2")
    )


# FriendRequest 表
class FriendRequest(TimestampMixin, table=True):
    RequestID: Optional[int] = Field(default=None, primary_key=True)
    SenderID: uuid.UUID = Field(nullable=False)
    ReceiverID: uuid.UUID = Field(nullable=False)
    Status: Optional[StatusEnum] = Field(default="Pending")
    RequestDate: Optional[datetime] = Field(default_factory=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("SenderID", "ReceiverID"),
        ForeignKeyConstraint(["SenderID"], ["user.UserID"], name="fk_friendrequest_user1"),
        ForeignKeyConstraint(["ReceiverID"], ["user.UserID"], name="fk_friendrequest_user2")
    )


# BlockList 表
class BlockList(TimestampMixin, table=True):
    BlockID: Optional[int] = Field(default=None, primary_key=True)
    BlockerID: uuid.UUID = Field(nullable=False)
    BlockedID: uuid.UUID = Field(nullable=False)
    BlockDate: Optional[datetime] = Field(default_factory=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("BlockerID", "BlockedID"),
        ForeignKeyConstraint(["BlockerID"], ["user.UserID"], name="fk_blocklist_user1"),
        ForeignKeyConstraint(["BlockedID"], ["user.UserID"], name="fk_blocklist_user2")
    )


# Detection 表
class Detection(TimestampMixin, table=True):
    DetectionID: Optional[int] = Field(default=None, primary_key=True)
    UserID: uuid.UUID = Field(nullable=False)
    StartTime: datetime = Field(nullable=False)
    EndTime: datetime = Field(nullable=False)
    TotalTime: time = Field(nullable=False)
    TotalPredictions: int = Field(nullable=False)
    Score: float = Field(nullable=False)

    __table_args__ = (
        ForeignKeyConstraint(["UserID"], ["user.UserID"], name="fk_detection_user"),
    )

# BodyPartMixin：共用的部位欄位
class BodyPartMixin(SQLModel):
    DetectionID: int = Field(primary_key=True)
    PredictionCount: Optional[int] = Field(default=0)
    PartialScore: Optional[float] = None

# Head 表
class Head(BodyPartMixin, table=True):
    BowedCount: Optional[int] = Field(default=0)
    NeutralCount: Optional[int] = Field(default=0)
    TiltBackCount: Optional[int] = Field(default=0)

    __table_args__ = (
        ForeignKeyConstraint(["DetectionID"], ["detection.DetectionID"], name="fk_head_detection"),
    )

# Neck 表
class Neck(BodyPartMixin, table=True):
    ForwardCount: Optional[int] = Field(default=0)
    NeutralCount: Optional[int] = Field(default=0)

    __table_args__ = (
        ForeignKeyConstraint(["DetectionID"], ["detection.DetectionID"], name="fk_neck_detection"),
    )

# Shoulder 表
class Shoulder(BodyPartMixin, table=True):
    HunchedCount: Optional[int] = Field(default=0)
    NeutralCount: Optional[int] = Field(default=0)
    ShrugCount: Optional[int] = Field(default=0)

    __table_args__ = (
        ForeignKeyConstraint(["DetectionID"], ["detection.DetectionID"], name="fk_shoulder_detection"),
    )

# Torso 表
class Torso(BodyPartMixin, table=True):
    BackwardCount: Optional[int] = Field(default=0)
    ForwardCount: Optional[int] = Field(default=0)
    NeutralCount: Optional[int] = Field(default=0)

    __table_args__ = (
        ForeignKeyConstraint(["DetectionID"], ["detection.DetectionID"], name="fk_torso_detection"),
    )

# Feet 表
class Feet(BodyPartMixin, table=True):
    AnkleOnKneeCount: Optional[int] = Field(default=0)
    FlatCount: Optional[int] = Field(default=0)

    __table_args__ = (
        ForeignKeyConstraint(["DetectionID"], ["detection.DetectionID"], name="fk_feet_detection"),
    )