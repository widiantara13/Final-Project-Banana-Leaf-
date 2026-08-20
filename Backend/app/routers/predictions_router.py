from fastapi import APIRouter, HTTPException, status, Request, File, UploadFile
from sqlalchemy import insert, delete
from typing import List
from app.models.predictions_model import Predictions
from app.utils.log_activity_util import record_activity, get_browser, get_ip
from app.schemas.log_activity_schema import Log_Activity_Schema
from app.schemas.predict_schema import History, DoPredict
from app.depedencies.db_dependency import db_dependency
from app.depedencies.user_dependency import is_admin_depend, user_depend
from app.utils.models_utils import predict
from app.utils.image_utils import image_saver, image_delete
from app.models.leaf_conditon_model import LeafCondition


from sqlalchemy.future import select
from sqlalchemy.orm import selectinload





predic = APIRouter(
    prefix = "/predict",
    tags = ["predict"],
    responses = {404: {"description": "not found"}}
)

@predic.get("/show", response_model=List[History], status_code=200)
async def show_predict(user: user_depend, db: db_dependency):
    try:
        if user:
            stmt = (
                select(
                    Predictions.id,
                    Predictions.image_path,
                    Predictions.confidence,
                    LeafCondition.condition.label("condition")  # ambil field dari tabel relasi
                )
                .join(LeafCondition, Predictions.leaf_condition_id == LeafCondition.id)
                .where(Predictions.owner_id == user.id)
            )
            result = await db.execute(stmt)
            rows = result.all()
            if not rows:
                raise HTTPException(status_code=404, detail="data tidak ditemukan")

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


@predic.post("/add", status_code = status.HTTP_201_CREATED)
async def add_predict(user: user_depend, db: db_dependency,
                      request: Request,file: UploadFile = File(...)):
    try:
       if user:
            pred  = await predict(file)
            if pred["class"] == "random":
                return{"detail":f"Gambar yang anda inputkan bukan daun pisang, dengan presentase{pred['confidence']}"}
            image_path =image_saver(file, "predict")
            
            smt = insert(Predictions).values(
                owner_id = user.id,
                image_path = image_path,
                leaf_condition_id = pred["index"],                
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
            
            
            

            return {"detail": "success", "data": result}
    except Exception as e:
        await db.rollback()
        print(f"Detail error: {repr(e)}")
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
                                    detail = f"terjadi kesalahan internal")

@predic.delete("/delete/{id_predict}", status_code = status.HTTP_200_OK)
async def delete_predict(user: user_depend, db: db_dependency, id_predict: int, request: Request):
    try:
        if user:
            get_predict = await show_predict_detail(user, db, id_predict)
            if get_predict is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                    detail="data tidak ditemukan")
            await image_delete(get_predict.image_path)
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

            
    
        
