from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models import Record, Body, Feet, Head, Shoulder, Neck
from app.schemas import UserResponse, RecordCreate, RecordResponse, BodyCreate, FeetCreate, HeadCreate, ShoulderCreate, NeckCreate
from app.core.database import get_db
from app.dependencies import get_current_user
from typing import List, Annotated

router = APIRouter()

@router.post("/", response_model=RecordResponse)
async def create_record(
    record: RecordCreate,
    current_user: Annotated[UserResponse, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    new_record = Record(
        UserID=current_user.UserID,
        StartTime=record.StartTime,
        EndTime=record.EndTime,
        TotalTime=record.TotalTime,
        TotalPredictions=record.TotalPredictions
    )
    try:
        db.add(new_record)
        db.commit()
        db.refresh(new_record)

        # 創建對應的部位紀錄
        body = Body(RecordID=new_record.RecordID, **record.Body.dict())
        feet = Feet(RecordID=new_record.RecordID, **record.Feet.dict())
        head = Head(RecordID=new_record.RecordID, **record.Head.dict())
        shoulder = Shoulder(RecordID=new_record.RecordID, **record.Shoulder.dict())
        neck = Neck(RecordID=new_record.RecordID, **record.Neck.dict())

        db.add(body)
        db.add(feet)
        db.add(head)
        db.add(shoulder)
        db.add(neck)
        db.commit()
    except:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create record")
    
    return RecordResponse(
        RecordID=new_record.RecordID,
        UserID=new_record.UserID,
        TotalPredictions=new_record.TotalPredictions,
        StartTime=str(new_record.StartTime),  # 轉換為字串
        EndTime=str(new_record.EndTime),      # 轉換為字串
        TotalTime=str(new_record.TotalTime),  # 轉換為字串
        Body=record.Body,                         # 確保這些欄位存在
        Feet=record.Feet,
        Head=record.Head,
        Shoulder=record.Shoulder,
        Neck=record.Neck,
    )

@router.get("/", response_model=List[RecordResponse])
async def get_records(
    current_user: Annotated[UserResponse, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    records = db.query(Record).filter(Record.UserID == current_user.UserID).all()
    responses = []
    for record in records:
        body = db.query(Body).filter(Body.RecordID == record.RecordID).first()
        feet = db.query(Feet).filter(Feet.RecordID == record.RecordID).first()
        head = db.query(Head).filter(Head.RecordID == record.RecordID).first()
        shoulder = db.query(Shoulder).filter(Shoulder.RecordID == record.RecordID).first()
        neck = db.query(Neck).filter(Neck.RecordID == record.RecordID).first()
        responses.append(RecordResponse(
            RecordID=record.RecordID,
            UserID=record.UserID,
            StartTime=str(record.StartTime),
            EndTime=str(record.EndTime),
            TotalTime=str(record.TotalTime),
            TotalPredictions=record.TotalPredictions,
            Body=BodyCreate.from_orm(body) if body else BodyCreate(),
            Feet=FeetCreate.from_orm(feet) if feet else FeetCreate(),
            Head=HeadCreate.from_orm(head) if head else HeadCreate(),
            Shoulder=ShoulderCreate.from_orm(shoulder) if shoulder else ShoulderCreate(),
            Neck=NeckCreate.from_orm(neck) if neck else NeckCreate()
        ))
    return responses

@router.get("/{record_id}", response_model=RecordResponse)
async def get_record(
    record_id: int,
    current_user: Annotated[UserResponse, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    record = db.query(Record).filter(Record.RecordID == record_id, Record.UserID == current_user.UserID).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")

    # 獲取對應的部位資料
    body = db.query(Body).filter(Body.RecordID == record_id).first()
    feet = db.query(Feet).filter(Feet.RecordID == record_id).first()
    head = db.query(Head).filter(Head.RecordID == record_id).first()
    shoulder = db.query(Shoulder).filter(Shoulder.RecordID == record_id).first()
    neck = db.query(Neck).filter(Neck.RecordID == record_id).first()

    return RecordResponse(
        RecordID=record.RecordID,
        UserID=record.UserID,
        StartTime=str(record.StartTime),
        EndTime=str(record.EndTime),
        TotalTime=str(record.TotalTime),
        TotalPredictions=record.TotalPredictions,
        Body=BodyCreate.from_orm(body),
        Feet=FeetCreate.from_orm(feet),
        Head=HeadCreate.from_orm(head),
        Shoulder=ShoulderCreate.from_orm(shoulder),
        Neck=NeckCreate.from_orm(neck)
    )

@router.put("/{record_id}", response_model=RecordResponse)
async def update_record(
    record_id: int,
    record: RecordCreate,
    current_user: Annotated[UserResponse, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    db_record = db.query(Record).filter(Record.RecordID == record_id, Record.UserID == current_user.UserID).first()
    if not db_record:
        raise HTTPException(status_code=404, detail="Record not found")
    
    db_record.StartTime = record.StartTime
    db_record.EndTime = record.EndTime  
    db_record.TotalTime = record.TotalTime
    db_record.TotalPredictions = record.TotalPredictions

    try:
        db.commit()
        db.refresh(db_record)
        # 更新對應的部位紀錄
        # synchronize_session="fetch" 確保更新後的資料立即反映在資料庫中:TBU
        # https://stackoverflow.com/questions/70350298/what-does-synchronize-session-false-do-exactly-in-update-functions-for-sqlalch
        db.query(Body).filter(Body.RecordID == record_id).update(record.Body.dict(), synchronize_session="fetch")
        db.query(Feet).filter(Feet.RecordID == record_id).update(record.Feet.dict(), synchronize_session="fetch")
        db.query(Head).filter(Head.RecordID == record_id).update(record.Head.dict(), synchronize_session="fetch")
        db.query(Shoulder).filter(Shoulder.RecordID == record_id).update(record.Shoulder.dict(), synchronize_session="fetch")
        db.query(Neck).filter(Neck.RecordID == record_id).update(record.Neck.dict(), synchronize_session="fetch")
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update record: {str(e)}")

    return RecordResponse(
        RecordID=record_id,
        UserID=db_record.UserID,
        StartTime=str(db_record.StartTime),
        EndTime=str(db_record.EndTime),
        TotalTime=str(db_record.TotalTime),
        TotalPredictions=db_record.TotalPredictions,
        Body=record.Body,
        Feet=record.Feet,
        Head=record.Head,
        Shoulder=record.Shoulder,
        Neck=record.Neck
    )

@router.delete("/{record_id}", response_model=dict)
async def delete_record(
    record_id: int,
    current_user: Annotated[UserResponse, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    db_record = db.query(Record).filter(Record.RecordID == record_id, Record.UserID == current_user.UserID).first()
    if not db_record:
        raise HTTPException(status_code=404, detail="Record not found")
    try:
        # 刪除對應的部位紀錄
        db.query(Body).filter(Body.RecordID == record_id).delete()
        db.query(Feet).filter(Feet.RecordID == record_id).delete()
        db.query(Head).filter(Head.RecordID == record_id).delete()
        db.query(Shoulder).filter(Shoulder.RecordID == record_id).delete()
        db.query(Neck).filter(Neck.RecordID == record_id).delete()

        db.delete(db_record)
        db.commit()
    except:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to delete record")
    
    return {"detail": "Record deleted successfully"}