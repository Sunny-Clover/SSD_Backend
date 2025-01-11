from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.models import User, Detection, Torso, Feet, Head, Shoulder, Neck
from app.schemas import UserResponse, DetectionCreate, DetectionResponse, TorsoCreate, FeetCreate, HeadCreate, ShoulderCreate, NeckCreate
from app.api.deps import CurrentUser, SessionDep
from typing import List, Annotated
from datetime import datetime, timedelta

router = APIRouter()

@router.post("/", response_model=DetectionResponse, status_code=status.HTTP_201_CREATED)
def create_detection(
    detection_data: DetectionCreate,
    db: SessionDep,
    current_user: CurrentUser
):
    # 計算 PartialScore
    def calculate_partial_score(correct_count, total_predictions):
        return correct_count / total_predictions if total_predictions > 0 else 0.0

    # 計算每個部位的 PartialScore
    torso_score = calculate_partial_score(detection_data.Torso.NeutralCount, detection_data.TotalPredictions)
    feet_score = calculate_partial_score(detection_data.Feet.FlatCount, detection_data.TotalPredictions)
    head_score = calculate_partial_score(detection_data.Head.NeutralCount, detection_data.TotalPredictions)
    shoulder_score = calculate_partial_score(detection_data.Shoulder.NeutralCount, detection_data.TotalPredictions)
    neck_score = calculate_partial_score(detection_data.Neck.NeutralCount, detection_data.TotalPredictions)

    # 計算 Single Detection Score
    detection_score = (torso_score + feet_score + head_score + shoulder_score + neck_score) / 5.0

    # 創建 Detection 記錄
    new_detection = Detection(
        UserID=current_user.UserID,
        StartTime=detection_data.StartTime,
        EndTime=detection_data.EndTime,
        TotalTime=detection_data.TotalTime,
        TotalPredictions=detection_data.TotalPredictions,
        Score=detection_score
    )
    db.add(new_detection)
    db.commit()
    db.refresh(new_detection)

    # 創建每個部位的紀錄
    body_parts = {
        "Torso": Torso(
            DetectionID=new_detection.DetectionID,
            BackwardCount=detection_data.Torso.BackwardCount,
            ForwardCount=detection_data.Torso.ForwardCount,
            NeutralCount=detection_data.Torso.NeutralCount,
            AmbiguousCount=detection_data.Torso.AmbiguousCount,
            PartialScore=torso_score
        ),
        "Feet": Feet(
            DetectionID=new_detection.DetectionID,
            AnkleOnKneeCount=detection_data.Feet.AnkleOnKneeCount,
            FlatCount=detection_data.Feet.FlatCount,
            AmbiguousCount=detection_data.Torso.AmbiguousCount,
            PartialScore=feet_score
        ),
        "Head": Head(
            DetectionID=new_detection.DetectionID,
            BowedCount=detection_data.Head.BowedCount,
            NeutralCount=detection_data.Head.NeutralCount,
            TiltBackCount=detection_data.Head.TiltBackCount,
            AmbiguousCount=detection_data.Torso.AmbiguousCount,
            PartialScore=head_score
        ),
        "Shoulder": Shoulder(
            DetectionID=new_detection.DetectionID,
            HunchedCount=detection_data.Shoulder.HunchedCount,
            NeutralCount=detection_data.Shoulder.NeutralCount,
            ShrugCount=detection_data.Shoulder.ShrugCount,
            AmbiguousCount=detection_data.Torso.AmbiguousCount,
            PartialScore=shoulder_score
        ),
        "Neck": Neck(
            DetectionID=new_detection.DetectionID,
            ForwardCount=detection_data.Neck.ForwardCount,
            NeutralCount=detection_data.Neck.NeutralCount,
            AmbiguousCount=detection_data.Torso.AmbiguousCount,
            PartialScore=neck_score
        ),
    }

    # 新增部位資料到資料庫
    for part in body_parts.values():
        db.add(part)
    # region: 更新 User 資料
    db_user = db.query(User).filter(User.UserID == current_user.UserID).first()
    if db_user:
        # 更新 User 的 AllTimeScore 跟 TotalPredictionCount
        total_weight_after = (db_user.AllTimeScore * db_user.TotalPredictionCount) \
                           + (detection_score * detection_data.TotalPredictions)
        total_prediction_count_after = db_user.TotalPredictionCount + detection_data.TotalPredictions
        db_user.AllTimeScore = total_weight_after / total_prediction_count_after
        db_user.TotalPredictionCount = total_prediction_count_after

        # 更新 User 的 TotalDetectionTime
        new_detection_time = datetime.combine(datetime.min, db_user.TotalDetectionTime) + timedelta(
            hours=detection_data.TotalTime.hour,
            minutes=detection_data.TotalTime.minute,
            seconds=detection_data.TotalTime.second
        )
        db_user.TotalDetectionTime = new_detection_time.time()
    db.commit()
    db.refresh(new_detection) #commit過後重新refresh一遍
    # endregion


    # TODO: 只能先這樣，還找不到解決Pydantic不能轉換nested的原因，我覺得可能是因為Detection的head是Relationship
    detection_response = DetectionResponse(
        **new_detection.dict(),
        Head = new_detection.head,
        Neck = new_detection.neck,
        Shoulder = new_detection.shoulder,
        Torso = new_detection.torso,
        Feet = new_detection.feet,
    )
    return detection_response

# 保留：還需要測試一下
@router.get("/", response_model=List[DetectionResponse])
def get_detections(
    db: SessionDep,
    current_user: CurrentUser
):
    detections = db.query(Detection).filter(Detection.UserID == current_user.UserID).all()
    deteciton_response = []
    for detection in detections:
        deteciton_response.append(DetectionResponse(
            **detection.dict(),
            Head = detection.head,
            Neck = detection.neck,
            Shoulder = detection.shoulder,
            Torso = detection.torso,
            Feet = detection.feet,
        ))
    return deteciton_response


@router.get("/{detection_id}", response_model=DetectionResponse)
def get_Detection(
    detection_id: int,
    current_user: CurrentUser,
    db: SessionDep
):
    detection = db.query(Detection).filter(Detection.DetectionID == detection_id, Detection.UserID == current_user.UserID).first()
    
    if not detection:
        raise HTTPException(status_code=404, detail="Detection not found")

    return DetectionResponse(
                **detection.dict(),
                Head = detection.head,
                Neck = detection.neck,
                Shoulder = detection.shoulder,
                Torso = detection.torso,
                Feet = detection.feet
                )
# region: [API] put and delete not avaliable now
'''
@router.put("/{Detection_id}", response_model=DetectionResponse)
def update_Detection(
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
def delete_Detection(
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
'''
# endregion 
