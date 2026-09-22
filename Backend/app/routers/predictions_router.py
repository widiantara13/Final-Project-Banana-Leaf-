from fastapi import APIRouter, HTTPException, status, Request, File, UploadFile
from sqlalchemy import insert, delete
from typing import List, Optional
from app.models.predictions_model import Predictions
from app.models.users_model import Users
from app.utils.log_activity_util import record_activity, get_browser, get_ip
from app.schemas.log_activity_schema import Log_Activity_Schema
from app.schemas.predict_schema import History, DoPredict, AdminPredictionHistory
from app.depedencies.db_dependency import db_dependency
from app.depedencies.user_dependency import is_admin_depend, user_depend
from app.utils.models_utils import predict
from app.utils.image_utils import image_saver, image_delete
from app.models.leaf_conditon_model import LeafCondition
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate

from sqlalchemy.future import select
from sqlalchemy.orm import selectinload





predic = APIRouter(
    prefix = "/predict",
    tags = ["predict"],
    responses = {404: {"description": "not found"}}
)

@predic.get("/show-all", response_model=Page[AdminPredictionHistory], status_code=status.HTTP_200_OK)
async def show_all_predictions(
    admin: is_admin_depend,
    db: db_dependency,
    email: Optional[str] = None
) -> Page[AdminPredictionHistory]:
    try:
        if admin:
            stmt = (
                select(
                    Predictions.id,
                    Predictions.image_path,
                    Predictions.confidence,
                    Predictions.created_at,
                    LeafCondition.condition.label("condition"),
                    Users.email.label("email")
                )
                .join(LeafCondition, Predictions.leaf_condition_id == LeafCondition.id)
                .join(Users, Predictions.owner_id == Users.id)
            )
            if email and email.strip():
                stmt = stmt.where(Users.email.ilike(f"%{email.strip()}%"))
            stmt = stmt.order_by(Predictions.created_at.desc())
            return await paginate(db, stmt)
    except Exception as e:
        print(f"Detail error: {repr(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="terjadi kesalahan internal")

@predic.get("/show", response_model=List[History], status_code=200)
async def show_predict(user: user_depend, db: db_dependency):
    try:
        if user:
            stmt = (
                select(
                    Predictions.id,
                    Predictions.image_path,
                    Predictions.confidence,
                    Predictions.created_at,
                    LeafCondition.condition.label("condition")  # ambil field dari tabel relasi
                )
                .join(LeafCondition, Predictions.leaf_condition_id == LeafCondition.id)
                .where(Predictions.owner_id == user.id)
                .order_by(Predictions.created_at.desc())
            )
            result = await db.execute(stmt)
            rows = result.all()
            if not rows:
                return []

            # convert ke dict agar cocok dengan schema History
            return [dict(row._mapping) for row in rows]
    except HTTPException:
        raise
    except Exception as e:
        print(f"Detail error: {repr(e)}")
        raise HTTPException(status_code=500, detail="terjadi kesalahan internal")

@predic.get("/show/{id_predict}", response_model = History, status_code = status.HTTP_200_OK)
async def show_predict_detail(user: user_depend, db: db_dependency, id_predict: int):
    try:
        if user:
            get_predict = await db.execute(select(Predictions.id, 
                                                Predictions.image_path,
                                                LeafCondition.condition,
                                                Predictions.confidence).
                                                where(Predictions.id == id_predict).
                                                join(LeafCondition,
                                                Predictions.leaf_condition_id == LeafCondition.id))
            pred =  get_predict.first()
            if not pred:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                    detail="data tidak ditemukan")
            return dict(pred._mapping)
    except HTTPException:
        raise
    except Exception as e:
        print(f"Detail error: {repr(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="terjadi kesalahan internal")


@predic.get("/status", status_code=status.HTTP_200_OK)
async def check_model_readiness(user: user_depend):
    try:
        if user:
            from app.utils.models_utils import model_filter, model_diseases
            is_ready = (model_filter is not None) and (model_diseases is not None)
            return {
                "is_ready": is_ready,
                "message": (
                    "Model siap digunakan"
                    if is_ready
                    else "Model deteksi belum aktif, mohon tunggu beberapa saat lagi atau hubungi administrator"
                ),
                "filter_ready": model_filter is not None,
                "diseases_ready": model_diseases is not None,
            }
    except Exception as e:
        print(f"Detail error: {repr(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="terjadi kesalahan internal saat memeriksa kesiapan model"
        )

@predic.post("/add", status_code = status.HTTP_201_CREATED)
async def add_predict(user: user_depend, db: db_dependency,
                      request: Request,file: UploadFile = File(...)):
    try:
       if user:
            pred  = await predict(file)
            if pred["class"] == "random":
                record = Log_Activity_Schema(
                    action = f"Membuat prediksi dengan hasil bukan daun pisang dan confidence {pred['confidence']}",
                    module = "predictions_router",
                    user_id = user.id,
                    email = user.email,
                    ip = get_ip(request),
                    browser = get_browser(request)
                )
                await record_activity(
                    db,
                    record
                )
                return {"detail": f"Gambar yang anda inputkan bukan daun pisang, dengan persentase {pred['confidence']}"}
            image_path =image_saver(file, "predict")
            
            smt = insert(Predictions).values(
                owner_id = user.id,
                image_path = image_path,
                leaf_condition_id = pred["index"]+1 ,                
                confidence = pred["confidence"]
            )
            save_pred = await db.execute(smt)

            
            record = Log_Activity_Schema(
                action = f"Membuat prediksi dengan hasil {pred['class']} dan confidence {pred['confidence']}",
                module = "predictions_router",
                user_id = user.id,
                email = user.email,
                ip = get_ip(request),
                browser = get_browser(request)
            )
            await record_activity(
                db,
                record
            )
            
        

            await db.commit()
            new_id = save_pred.lastrowid
            result = await show_predict_detail(user, db, new_id)
            
            
            

            return {"detail": "success", "data": result, "real":pred["class"]}
    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        print(f"Detail error: {repr(e)}")
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail = "terjadi kesalahan internal")

@predic.delete("/delete/{id_predict}", status_code = status.HTTP_200_OK)
async def delete_predict(user: user_depend, db: db_dependency, id_predict: int, request: Request):
    try:
        if user:
            get_predict = await show_predict_detail(user, db, id_predict)
            if get_predict is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                    detail="data tidak ditemukan")
            img_path = get_predict.get("image_path") if isinstance(get_predict, dict) else getattr(get_predict, "image_path", None)
            if img_path:
                image_delete(img_path)
            smt = delete(Predictions).where(Predictions.id == id_predict)
            await db.execute(smt)
            record = Log_Activity_Schema(
                action = f"Menghapus prediksi dengan id {id_predict}",
                module = "predictions_router",
                user_id = user.id,
                email = user.email,
                ip = get_ip(request),
                browser = get_browser(request)
            )
            await record_activity(
                db,
                record
            )
            await db.commit()
            return {"detail": "success"}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Detail error: {repr(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="terjadi kesalahan internal")

            
    
        
