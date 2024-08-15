from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.models import User, FriendList, FriendRequest
from app.schemas import UserResponse, FriendRequestCreate, FriendRequestResponse, SuccessMessage, FriendRequestAction
from app.core.database import get_db
from app.dependencies import get_current_user
from typing import List, Annotated

router = APIRouter()

@router.get("/", response_model=List[UserResponse])
async def get_friends_list(
    current_user: Annotated[UserResponse, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    friends = db.query(User).join(FriendList, (FriendList.UserID1 == User.UserID) | (FriendList.UserID2 == User.UserID))\
        .filter(
            ((FriendList.UserID1 == current_user.UserID) | (FriendList.UserID2 == current_user.UserID)) &
            (FriendList.Status == 'Accepted') &
            (User.UserID != current_user.UserID)
        ).all()

    return [UserResponse.from_orm(friend) for friend in friends]

@router.post("/request", response_model=SuccessMessage)
async def send_friend_request(
    request: FriendRequestCreate,
    current_user: Annotated[UserResponse, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    # 檢查接收者是否存在
    receiver = db.query(User).filter(User.UserID == request.ReceiverID).first()
    if not receiver:
        raise HTTPException(status_code=404, detail="接收者不存在")

    # 檢查是否已經是好友
    existing_friendship = db.query(FriendList).filter(
        ((FriendList.UserID1 == current_user.UserID) & (FriendList.UserID2 == request.ReceiverID)) |
        ((FriendList.UserID1 == request.ReceiverID) & (FriendList.UserID2 == current_user.UserID))
    ).first()
    if existing_friendship:
        raise HTTPException(status_code=400, detail="已經是好友")

    # 檢查是否已經發送過請求
    existing_request = db.query(FriendRequest).filter(
        (FriendRequest.SenderID == current_user.UserID) &
        (FriendRequest.ReceiverID == request.ReceiverID)
    ).first()
    if existing_request:
        raise HTTPException(status_code=400, detail="已經發送過好友請求")

    # 創建新的好友請求
    new_request = FriendRequest(
        SenderID=current_user.UserID,
        ReceiverID=request.ReceiverID
    )
    db.add(new_request)
    db.commit()

    return SuccessMessage(message="好友請求已發送")

@router.get("/requests", response_model=List[FriendRequestResponse])
async def get_friend_requests(
    current_user: Annotated[UserResponse, Depends(get_current_user)],
    db: Session = Depends(get_db),
    request_type: str = Query(..., description="請求類型：'received' 或 'sent'")
):
    if request_type not in ['received', 'sent']:
        raise HTTPException(status_code=400, detail="無效的請求類型")

    query = db.query(FriendRequest, User.UserName)
    
    if request_type == 'received':  # JOIN並取出sender的username
        query = query.join(User, FriendRequest.SenderID == User.UserID)\
            .filter(FriendRequest.ReceiverID == current_user.UserID)
    else:  # JOIN並取出receiver的username
        query = query.join(User, FriendRequest.ReceiverID == User.UserID)\
            .filter(FriendRequest.SenderID == current_user.UserID)
    
    requests = query.filter(FriendRequest.Status == 'Pending').all()

    return [
        FriendRequestResponse(
            RequestID=req.RequestID,
            SenderID=req.SenderID,
            SenderUserName=current_user.UserName if request_type == 'sent' else username,
            ReceiverID=req.ReceiverID,
            ReceiverUserName=username if request_type == 'sent' else current_user.UserName,
            Status=req.Status,
            RequestDate=str(req.RequestDate)
        ) for req, username in requests
    ]

@router.post("/requests/{request_id}/action", response_model=SuccessMessage)
async def handle_friend_request(
    request_id: int,
    action: FriendRequestAction,
    current_user: Annotated[UserResponse, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    friend_request = db.query(FriendRequest).filter(
        FriendRequest.RequestID == request_id,
        FriendRequest.ReceiverID == current_user.UserID,
        FriendRequest.Status == 'Pending'
    ).first()

    if not friend_request:
        raise HTTPException(status_code=404, detail="好友請求不存在或已處理")

    if action.Action == 'accept':
        friend_request.Status = 'Accepted'
        message = "好友請求已接受"
    elif action.Action == 'decline':
        friend_request.Status = 'Declined'
        message = "好友請求已拒絕"
    else:
        raise HTTPException(status_code=400, detail="無效的操作")

    db.commit()
    return SuccessMessage(message=message)