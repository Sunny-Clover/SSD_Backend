from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models import Detection, Torso, Feet, Head, Shoulder, Neck
from app.schemas import UserResponse, DetectionCreate, DetectionResponse, TorsoCreate, FeetCreate, HeadCreate, ShoulderCreate, NeckCreate
from app.api.deps import CurrentUser, SessionDep
from typing import List, Annotated

router = APIRouter()

@router.post("/", response_model=DetectionResponse)
async def create_Detection(
    Detection: DetectionCreate,
    current_user: CurrentUser,
    db: SessionDep
):
    new_Detection = Detection(
        UserID=current_user.UserID,
        StartTime=Detection.StartTime,
        EndTime=Detection.EndTime,
        TotalTime=Detection.TotalTime,
        TotalPredictions=Detection.TotalPredictions
    )
    try:
        db.add(new_Detection)
        db.commit()
        db.refresh(new_Detection)

        # 創建對應的部位紀錄
        Torso = Torso(DetectionID=new_Detection.DetectionID, **Detection.Torso.dict())
        feet = Feet(DetectionID=new_Detection.DetectionID, **Detection.Feet.dict())
        head = Head(DetectionID=new_Detection.DetectionID, **Detection.Head.dict())
        shoulder = Shoulder(DetectionID=new_Detection.DetectionID, **Detection.Shoulder.dict())
        neck = Neck(DetectionID=new_Detection.DetectionID, **Detection.Neck.dict())

        db.add(Torso)
        db.add(feet)
        db.add(head)
        db.add(shoulder)
        db.add(neck)
        db.commit()
    except:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create Detection")
    
    return DetectionResponse(
        DetectionID=new_Detection.DetectionID,
        UserID=new_Detection.UserID,
        TotalPredictions=new_Detection.TotalPredictions,
        StartTime=str(new_Detection.StartTime),  # 轉換為字串
        EndTime=str(new_Detection.EndTime),      # 轉換為字串
        TotalTime=str(new_Detection.TotalTime),  # 轉換為字串
        Torso=Detection.Torso,                         # 確保這些欄位存在
        Feet=Detection.Feet,
        Head=Detection.Head,
        Shoulder=Detection.Shoulder,
        Neck=Detection.Neck,
    )

@router.get("/", response_model=List[DetectionResponse])
async def get_Detections(
    current_user: CurrentUser,
    db: SessionDep
):
    Detections = db.query(Detection).filter(Detection.UserID == current_user.UserID).all()
    responses = []
    for Detection in Detections:
        Torso = db.query(Torso).filter(Torso.DetectionID == Detection.DetectionID).first()
        feet = db.query(Feet).filter(Feet.DetectionID == Detection.DetectionID).first()
        head = db.query(Head).filter(Head.DetectionID == Detection.DetectionID).first()
        shoulder = db.query(Shoulder).filter(Shoulder.DetectionID == Detection.DetectionID).first()
        neck = db.query(Neck).filter(Neck.DetectionID == Detection.DetectionID).first()
        responses.append(DetectionResponse(
            DetectionID=Detection.DetectionID,
            UserID=Detection.UserID,
            StartTime=str(Detection.StartTime),
            EndTime=str(Detection.EndTime),
            TotalTime=str(Detection.TotalTime),
            TotalPredictions=Detection.TotalPredictions,
            Torso=TorsoCreate.from_orm(Torso) if Torso else TorsoCreate(),
            Feet=FeetCreate.from_orm(feet) if feet else FeetCreate(),
            Head=HeadCreate.from_orm(head) if head else HeadCreate(),
            Shoulder=ShoulderCreate.from_orm(shoulder) if shoulder else ShoulderCreate(),
            Neck=NeckCreate.from_orm(neck) if neck else NeckCreate()
        ))
    return responses

@router.get("/{Detection_id}", response_model=DetectionResponse)
async def get_Detection(
    Detection_id: int,
    current_user: CurrentUser,
    db: SessionDep
):
    Detection = db.query(Detection).filter(Detection.DetectionID == Detection_id, Detection.UserID == current_user.UserID).first()
    if not Detection:
        raise HTTPException(status_code=404, detail="Detection not found")

    # 獲取對應的部位資料
    Torso = db.query(Torso).filter(Torso.DetectionID == Detection_id).first()
    feet = db.query(Feet).filter(Feet.DetectionID == Detection_id).first()
    head = db.query(Head).filter(Head.DetectionID == Detection_id).first()
    shoulder = db.query(Shoulder).filter(Shoulder.DetectionID == Detection_id).first()
    neck = db.query(Neck).filter(Neck.DetectionID == Detection_id).first()

    return DetectionResponse(
        DetectionID=Detection.DetectionID,
        UserID=Detection.UserID,
        StartTime=str(Detection.StartTime),
        EndTime=str(Detection.EndTime),
        TotalTime=str(Detection.TotalTime),
        TotalPredictions=Detection.TotalPredictions,
        Torso=TorsoCreate.from_orm(Torso),
        Feet=FeetCreate.from_orm(feet),
        Head=HeadCreate.from_orm(head),
        Shoulder=ShoulderCreate.from_orm(shoulder),
        Neck=NeckCreate.from_orm(neck)
    )

@router.put("/{Detection_id}", response_model=DetectionResponse)
async def update_Detection(
    Detection_id: int,
    Detection: DetectionCreate,
    current_user: CurrentUser,
    db: SessionDep
):
    db_Detection = db.query(Detection).filter(Detection.DetectionID == Detection_id, Detection.UserID == current_user.UserID).first()
    if not db_Detection:
        raise HTTPException(status_code=404, detail="Detection not found")
    
    db_Detection.StartTime = Detection.StartTime
    db_Detection.EndTime = Detection.EndTime  
    db_Detection.TotalTime = Detection.TotalTime
    db_Detection.TotalPredictions = Detection.TotalPredictions

    try:
        db.commit()
        db.refresh(db_Detection)
        # 更新對應的部位紀錄
        # synchronize_session="fetch" 確保更新後的資料立即反映在資料庫中:TBU
        # https://stackoverflow.com/questions/70350298/what-does-synchronize-session-false-do-exactly-in-update-functions-for-sqlalch
        db.query(Torso).filter(Torso.DetectionID == Detection_id).update(Detection.Torso.dict(), synchronize_session="fetch")
        db.query(Feet).filter(Feet.DetectionID == Detection_id).update(Detection.Feet.dict(), synchronize_session="fetch")
        db.query(Head).filter(Head.DetectionID == Detection_id).update(Detection.Head.dict(), synchronize_session="fetch")
        db.query(Shoulder).filter(Shoulder.DetectionID == Detection_id).update(Detection.Shoulder.dict(), synchronize_session="fetch")
        db.query(Neck).filter(Neck.DetectionID == Detection_id).update(Detection.Neck.dict(), synchronize_session="fetch")
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update Detection: {str(e)}")

    return DetectionResponse(
        DetectionID=Detection_id,
        UserID=db_Detection.UserID,
        StartTime=str(db_Detection.StartTime),
        EndTime=str(db_Detection.EndTime),
        TotalTime=str(db_Detection.TotalTime),
        TotalPredictions=db_Detection.TotalPredictions,
        Torso=Detection.Torso,
        Feet=Detection.Feet,
        Head=Detection.Head,
        Shoulder=Detection.Shoulder,
        Neck=Detection.Neck
    )

@router.delete("/{Detection_id}", response_model=dict)
async def delete_Detection(
    Detection_id: int,
    current_user: CurrentUser,
    db: SessionDep
):
    db_Detection = db.query(Detection).filter(Detection.DetectionID == Detection_id, Detection.UserID == current_user.UserID).first()
    if not db_Detection:
        raise HTTPException(status_code=404, detail="Detection not found")
    try:
        # 刪除對應的部位紀錄
        db.query(Torso).filter(Torso.DetectionID == Detection_id).delete()
        db.query(Feet).filter(Feet.DetectionID == Detection_id).delete()
        db.query(Head).filter(Head.DetectionID == Detection_id).delete()
        db.query(Shoulder).filter(Shoulder.DetectionID == Detection_id).delete()
        db.query(Neck).filter(Neck.DetectionID == Detection_id).delete()

        db.delete(db_Detection)
        db.commit()
    except:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to delete Detection")
    
    return {"detail": "Detection deleted successfully"}