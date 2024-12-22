from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import UniqueConstraint, ForeignKeyConstraint, Column, Integer, ForeignKey
from typing import Optional, List
from datetime import time, datetime
from enum import Enum


# 定義性別選項
class GenderEnum(str, Enum):
    Male = "Male"
    Female = "Female"
    Other = "Other"


# 定義好友請求狀態
class StatusEnum(str, Enum):
    Pending = "Pending"
    Accepted = "Accepted"
    Declined = "Declined"


# 基底類別：包含時間戳的共用欄位
class TimestampMixin(SQLModel):
    CreateDate: Optional[datetime] = Field(default_factory=datetime.utcnow, nullable=False)
    ModDate: Optional[datetime] = Field(default_factory=datetime.utcnow, nullable=False, sa_column_kwargs={"onupdate": datetime.utcnow})


# User 表
class UserBase(SQLModel):
    UserName: str = Field(max_length=50, nullable=False, unique=True)
    Email: str = Field(max_length=100, nullable=False, unique=True)
    FirstName: Optional[str] = Field(default='', max_length=50)
    LastName: Optional[str] = Field(default='', max_length=50)
    Gender: Optional[GenderEnum] = Field(default=GenderEnum.Other)
    PhotoUrl: Optional[str] = Field(default='', max_length=255)
    PostureAlertEnable: Optional[bool] = Field(default=False)
    PostureAlertTime: Optional[time] = Field(default=time(0, 0, 0))
    IdleAlertEnable: Optional[bool] = Field(default=False)
    IdleAlertTime: Optional[time] = Field(default=time(0, 0, 0))
    AllTimeScore: Optional[float] = Field(default=0.0)
    TotalDetectionTime: Optional[time] = Field(default=time(0, 0, 0))


class User(UserBase, TimestampMixin, table=True):
    UserID: int = Field(default=None, primary_key=True)
    Password: str = Field(max_length=255, nullable=False)

    detections: List["Detection"] = Relationship(back_populates="user")

# FriendList 表
class FriendList(TimestampMixin, table=True):
    FriendID: Optional[int] = Field(default=None, primary_key=True)
    UserID1: int = Field(nullable=False)
    UserID2: int = Field(nullable=False)

    __table_args__ = (
        UniqueConstraint("UserID1", "UserID2"),  # 使用 UniqueConstraint 來定義組合唯一約束
        ForeignKeyConstraint(["UserID1"], ["user.UserID"], name="fk_friendlist_user1"),
        ForeignKeyConstraint(["UserID2"], ["user.UserID"], name="fk_friendlist_user2")
    )


# FriendRequest 表
class FriendRequest(TimestampMixin, table=True):
    RequestID: Optional[int] = Field(default=None, primary_key=True)
    SenderID: int = Field(nullable=False)
    ReceiverID: int = Field(nullable=False)
    Status: Optional[StatusEnum] = Field(default=StatusEnum.Pending)
    RequestDate: Optional[datetime] = Field(default_factory=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("SenderID", "ReceiverID"),
        ForeignKeyConstraint(["SenderID"], ["user.UserID"], name="fk_friendrequest_user1"),
        ForeignKeyConstraint(["ReceiverID"], ["user.UserID"], name="fk_friendrequest_user2")
    )


# BlockList 表
class BlockList(TimestampMixin, table=True):
    BlockID: Optional[int] = Field(default=None, primary_key=True)
    BlockerID: int = Field(nullable=False)
    BlockedID: int = Field(nullable=False)
    BlockDate: Optional[datetime] = Field(default_factory=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("BlockerID", "BlockedID"),
        ForeignKeyConstraint(["BlockerID"], ["user.UserID"], name="fk_blocklist_user1"),
        ForeignKeyConstraint(["BlockedID"], ["user.UserID"], name="fk_blocklist_user2")
    )


# Detection 表
class Detection(TimestampMixin, table=True):
    DetectionID: Optional[int] = Field(default=None, primary_key=True)
    # UserID: int = Field(foreign_key='user.UserID', nullable=False)
    UserID: int = Field(
        sa_column=Column(
            Integer, 
            ForeignKey("user.UserID", name="fk_detection_userid"), 
            nullable=False
        )
    )
    StartTime: datetime = Field(nullable=False)
    EndTime: datetime = Field(nullable=False)
    TotalTime: time = Field(nullable=False)
    TotalPredictions: int = Field(nullable=False)
    Score: float = Field(nullable=False)

    # # 關聯到 User 表
    user: Optional[User] = Relationship(back_populates="detections")

    # 關聯到身體部位表
    head: Optional["Head"] = Relationship(back_populates="detection", sa_relationship_kwargs={"cascade": "all, delete"})
    neck: Optional["Neck"] = Relationship(back_populates="detection", sa_relationship_kwargs={"cascade": "all, delete"})
    shoulder: Optional["Shoulder"] = Relationship(back_populates="detection", sa_relationship_kwargs={"cascade": "all, delete"})
    torso: Optional["Torso"] = Relationship(back_populates="detection", sa_relationship_kwargs={"cascade": "all, delete"})
    feet: Optional["Feet"] = Relationship(back_populates="detection", sa_relationship_kwargs={"cascade": "all, delete"})


# BodyPartMixin：共用的部位欄位
class BodyPartMixin(SQLModel):
    # DetectionID: int = Field(primary_key=True)
    # PredictionCount: Optional[int] = Field(default=0)
    PartialScore: Optional[float] = Field(default=0.0)


# Head 表
class Head(BodyPartMixin, table=True):
    DetectionID: int = Field(
        sa_column=Column(
            Integer, 
            ForeignKey("detection.DetectionID", name="fk_head_detectionid"),
            primary_key=True
        )
    )
    BowedCount: Optional[int] = Field(default=0)
    NeutralCount: Optional[int] = Field(default=0)
    TiltBackCount: Optional[int] = Field(default=0)

    detection: Optional[Detection] = Relationship(back_populates="head")


# Neck 表
class Neck(BodyPartMixin, table=True):
    DetectionID: int = Field(
        sa_column=Column(
            Integer, 
            ForeignKey("detection.DetectionID", name="fk_neck_detectionid"),
            primary_key=True
        )
    )
    ForwardCount: Optional[int] = Field(default=0)
    NeutralCount: Optional[int] = Field(default=0)

    detection: Optional[Detection] = Relationship(back_populates="neck")


# Shoulder 表
class Shoulder(BodyPartMixin, table=True):
    DetectionID: int = Field(
        sa_column=Column(
            Integer, 
            ForeignKey("detection.DetectionID", name="fk_shoulder_detectionid"),
            primary_key=True
        )
    )
    HunchedCount: Optional[int] = Field(default=0)
    NeutralCount: Optional[int] = Field(default=0)
    ShrugCount: Optional[int] = Field(default=0)

    detection: Optional[Detection] = Relationship(back_populates="shoulder")


# Torso 表
class Torso(BodyPartMixin, table=True):
    DetectionID: int = Field(
        sa_column=Column(
            Integer, 
            ForeignKey("detection.DetectionID", name="fk_torso_detectionid"),
            primary_key=True
        )
    )
    BackwardCount: Optional[int] = Field(default=0)
    ForwardCount: Optional[int] = Field(default=0)
    NeutralCount: Optional[int] = Field(default=0)

    detection: Optional[Detection] = Relationship(back_populates="torso")


# Feet 表
class Feet(BodyPartMixin, table=True):
    DetectionID: int = Field(
        sa_column=Column(
            Integer, 
            ForeignKey("detection.DetectionID", name="fk_feet_detectionid"),
            primary_key=True
        )
    )
    AnkleOnKneeCount: Optional[int] = Field(default=0)
    FlatCount: Optional[int] = Field(default=0)

    detection: Optional[Detection] = Relationship(back_populates="feet")