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
    FirstName = Column(String(50), default='')
    LastName = Column(String(50), default='')
    Gender = Column(Enum('Male', 'Female', 'Other'), default='Other')
    PhotoUrl = Column(String(255), default='')
    InstantPostureAlertEnable = Column(Boolean, default=False)
    PostureAlertDelayTime = Column(Time, default='00:00:00')
    IdleAlertEnable = Column(Boolean, default=False)
    IdleAlertDelayTime = Column(Time, default='00:00:00')
    AverageScore = Column(Float, default=0.0)
    TotalTime = Column(Time, default='00:00:00')
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

class Record(Base):
    __tablename__ = 'Record'
    
    RecordID = Column(Integer, primary_key=True, autoincrement=True)
    UserID = Column(Integer, ForeignKey('User.UserID'), nullable=False)
    StartTime = Column(TIMESTAMP, nullable=False)
    EndTime = Column(TIMESTAMP, nullable=False)
    TotalTime = Column(Time, nullable=False)
    TotalPredictions = Column(Integer, nullable=False)
    CreateDate = Column(TIMESTAMP, server_default=func.now())
    ModDate = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

class Body(Base):
    __tablename__ = 'Body'
    
    RecordID = Column(Integer, ForeignKey('Record.RecordID'), primary_key=True)
    BackwardCount = Column(Integer, default=0)
    ForwardCount = Column(Integer, default=0)
    NeutralCount = Column(Integer, default=0)
    CreateDate = Column(TIMESTAMP, server_default=func.now())
    ModDate = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

class Feet(Base):
    __tablename__ = 'Feet'
    
    RecordID = Column(Integer, ForeignKey('Record.RecordID'), primary_key=True)
    AnkleOnKneeCount = Column(Integer, default=0)
    FlatCount = Column(Integer, default=0)
    CreateDate = Column(TIMESTAMP, server_default=func.now())
    ModDate = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

class Head(Base):
    __tablename__ = 'Head'
    
    RecordID = Column(Integer, ForeignKey('Record.RecordID'), primary_key=True)
    BowedCount = Column(Integer, default=0)
    NeutralCount = Column(Integer, default=0)
    TiltBackCount = Column(Integer, default=0)
    CreateDate = Column(TIMESTAMP, server_default=func.now())
    ModDate = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

class Shoulder(Base):
    __tablename__ = 'Shoulder'
    
    RecordID = Column(Integer, ForeignKey('Record.RecordID'), primary_key=True)
    HunchedCount = Column(Integer, default=0)
    NeutralCount = Column(Integer, default=0)
    ShrugCount = Column(Integer, default=0)
    CreateDate = Column(TIMESTAMP, server_default=func.now())
    ModDate = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

class Neck(Base):
    __tablename__ = 'Neck'
    
    RecordID = Column(Integer, ForeignKey('Record.RecordID'), primary_key=True)
    ForwardCount = Column(Integer, default=0)
    NeutralCount = Column(Integer, default=0)
    CreateDate = Column(TIMESTAMP, server_default=func.now())
    ModDate = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())