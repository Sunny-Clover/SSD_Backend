from sqlalchemy import Column, Integer, String, Enum, Boolean, Float, Time, TIMESTAMP, ForeignKey, UniqueConstraint, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class User(Base):
    __tablename__ = 'User'
    
    UserID = Column(Integer, primary_key=True, autoincrement=True)
    UserName = Column(String(50), unique=True, nullable=False)
    Email = Column(String(100), unique=True, nullable=False)
    Password = Column(String(255), nullable=False)
    FirstName = Column(String(50))
    LastName = Column(String(50))
    Gender = Column(Enum('Male', 'Female', 'Other'))
    PhotoUrl = Column(String(255))
    InstantPostureAlertEnable = Column(Boolean, default=False)
    PostureAlertDelayTime = Column(Time)
    IdleAlertEnable = Column(Boolean, default=False)
    IdleAlertDelayTime = Column(Time)
    AverageScore = Column(Float)
    TotalTime = Column(Time)
    CreateDate = Column(TIMESTAMP, server_default=func.now())
    ModDate = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

class FriendList(Base):
    __tablename__ = 'FriendList'
    
    FriendID = Column(Integer, primary_key=True, autoincrement=True)
    UserID1 = Column(Integer, ForeignKey('User.UserID'), nullable=False)
    UserID2 = Column(Integer, ForeignKey('User.UserID'), nullable=False)
    Status = Column(Enum('Pending', 'Accepted', 'Blocked'), default='Pending')
    RequestDate = Column(TIMESTAMP, server_default=func.now())
    CreateDate = Column(TIMESTAMP, server_default=func.now())
    ModDate = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        UniqueConstraint('UserID1', 'UserID2'),
    )

class FriendRequest(Base):
    __tablename__ = 'FriendRequest'
    
    RequestID = Column(Integer, primary_key=True, autoincrement=True)
    SenderID = Column(Integer, ForeignKey('User.UserID'), nullable=False)
    ReceiverID = Column(Integer, ForeignKey('User.UserID'), nullable=False)
    RequestDate = Column(TIMESTAMP, server_default=func.now())
    Status = Column(Enum('Pending', 'Accepted', 'Declined'), default='Pending')
    CreateDate = Column(TIMESTAMP, server_default=func.now())
    ModDate = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        UniqueConstraint('SenderID', 'ReceiverID'),
    )

class BlockedList(Base):
    __tablename__ = 'BlockedList'
    
    BlockID = Column(Integer, primary_key=True, autoincrement=True)
    BlockerID = Column(Integer, ForeignKey('User.UserID'), nullable=False)
    BlockedID = Column(Integer, ForeignKey('User.UserID'), nullable=False)
    BlockDate = Column(TIMESTAMP, server_default=func.now())
    CreateDate = Column(TIMESTAMP, server_default=func.now())
    ModDate = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        UniqueConstraint('BlockerID', 'BlockedID'),
    )
