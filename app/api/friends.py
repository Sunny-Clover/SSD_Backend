from fastapi import APIRouter, Depends, HTTPException, Query, status
from app.models import User, FriendList, FriendRequest, StatusEnum
from app.schemas import UserResponse, FriendRequestCreate, FriendRequestResponse, FriendRequestSentResponse, FriendRequestReceivedResponse, SuccessMessage, FriendRequestAction
from app.api.deps import get_current_user
from app.api.deps import CurrentUser, SessionDep
from typing import List, Annotated
from enum import Enum

router = APIRouter()


@router.get("/", response_model=List[UserResponse])
async def get_friends_list(
    current_user: CurrentUser,
    db: SessionDep
):
    friends = db.query(User)\
                .join(FriendList, FriendList.UserID2 == User.UserID)\
                .filter(FriendList.UserID1 == current_user.UserID)\
                .all()

    return friends

@router.post("/requests", response_model=SuccessMessage)
async def send_friend_request(
    request: FriendRequestCreate,
    current_user: CurrentUser,
    db: SessionDep
):
    # 不能加自己好友
    if request.ReceiverID == current_user.UserID:
        raise HTTPException(status_code=404, detail="不能加自己好友")
    # 檢查接收者是否存在
    receiver = db.query(User).filter(User.UserID == request.ReceiverID).first()
    if not receiver:
        raise HTTPException(status_code=404, detail="該用戶不存在")

    # 檢查是否已經是好友
    existing_friendship = db.query(FriendList) \
                            .filter(
                                (FriendList.UserID1 == current_user.UserID) &
                                (FriendList.UserID2 == request.ReceiverID)
                            ).first()
    if existing_friendship:
        raise HTTPException(status_code=400, detail="已成為好友")

    # 檢查是否已經發送過請求
    existing_request = db.query(FriendRequest).filter(
        (FriendRequest.SenderID == current_user.UserID) &
        (FriendRequest.ReceiverID == request.ReceiverID)
    ).first()
    # TODO: 這邊應該要給前端一隻檢核的API，然後判斷是不是可以重新請求
    if existing_request:
        raise HTTPException(status_code=400, detail="已發送過好友請求")

    # 創建新的好友請求
    new_request = FriendRequest(
        SenderID=current_user.UserID,
        ReceiverID=request.ReceiverID,
        Status=StatusEnum.Pending
    )
    db.add(new_request)
    db.commit()

    return SuccessMessage(message="好友請求已發送")

@router.get("/requests/received", response_model=List[FriendRequestReceivedResponse])
async def get_received_friend_requests(
    current_user: CurrentUser,
    db: SessionDep
):
    received_requests = db.query(
        FriendRequest.RequestID,
        FriendRequest.SenderID,
        User.UserName.label("SenderUserName"),
        FriendRequest.Status,
        FriendRequest.RequestDate
    ).join(User, User.UserID == FriendRequest.SenderID)\
     .filter(FriendRequest.ReceiverID == current_user.UserID)\
     .all()
    
    return received_requests

@router.get("/requests/sent", response_model=List[FriendRequestSentResponse])
async def get_sent_friend_requests(
    current_user: CurrentUser,
    db: SessionDep
):
    sent_requests = db.query(
        FriendRequest.RequestID,
        FriendRequest.ReceiverID,
        User.UserName.label("ReceiverUserName"),
        FriendRequest.Status,
        FriendRequest.RequestDate
    ).join(User, User.UserID == FriendRequest.ReceiverID)\
     .filter(FriendRequest.SenderID == current_user.UserID)\
     .all()
    
    return sent_requests

@router.patch("/requests/{id}", response_model=SuccessMessage)
async def handle_friend_request(
    id: int,
    action: FriendRequestAction,
    current_user: CurrentUser,
    db: SessionDep
):
    # 1. 查詢該好友請求
    friend_request = db.query(FriendRequest).filter(
        FriendRequest.RequestID == id,
        FriendRequest.ReceiverID == current_user.UserID  # 確保當前用戶是接收者
    ).first()

    if not friend_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="好友邀請不存在或無權處理"
        )

    if friend_request.Status != "Pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="好友邀請已處理"
        )

    # 2. 根據動作執行對應操作
    if action.Action == "Accept":
        friend_request.Status = "Accepted"
        # 加到好友清單
        db.add(FriendList(UserID1=current_user.UserID, UserID2=friend_request.SenderID))
        db.add(FriendList(UserID1=friend_request.SenderID, UserID2=current_user.UserID))
    elif action.Action == "Reject":
        friend_request.Status = "Declined"
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="無效的操作"
        )

    db.commit()

    return SuccessMessage(message=f"好友請求已{action.Action.lower()}")