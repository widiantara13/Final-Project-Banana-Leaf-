from app.schemas.leaf_condition_schema import Leaf_Condition, AddCondition, Detail_Leaf, Update_Leaf
from app.depedencies.db_dependency import db_dependency
from app.depedencies.user_dependency import is_admin_depend, user_depend
from app.schemas.log_activity_schema import Log_Activity_Schema
from app.utils.log_activity_util import record_activity, get_ip, get_browser
from sqlalchemy.exc import SQLAlchemyError
from app.models.leaf_conditon_model import LeafCondition
from starlette import status
from fastapi import APIRouter, HTTPException, Request, File, UploadFile, Form
from app.utils.image_utils import image_saver, image_delete
from sqlalchemy.future import select
from sqlalchemy import insert, update, delete
from typing import List



leafcon = APIRouter(
    prefix = "/leaf",
    tags = ["leaf conditon"],
    responses = {404: {"description": "not found"}}
)

@leafcon.get("/show/{id_leaf}", response_model = Detail_Leaf, status_code = status.HTTP_200_OK)
async def show_leaf_condition_detail(current_user: user_depend, db: db_dependency, id_leaf: int):
    try:
        if current_user:
            get_con = await db.execute(
                select(LeafCondition).where(id_leaf == LeafCondition.id)
            )
            result = get_con.scalars().first()

            if result is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="leaf condition tidak ditemukan"
                )

            return result

    except HTTPException as http_exc:
        # biarkan FastAPI tangani sesuai status code
        raise http_exc

    except SQLAlchemyError as db_err:
        print(f"DB error: {repr(db_err)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="kesalahan database"
        )

    except Exception as e:
        print(f"Detail error: {repr(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="terjadi kesalahan internal"
        )

@leafcon.get("/show", response_model = List[Leaf_Condition], status_code = status.HTTP_200_OK)
async def show_all_cond(current_user: user_depend, db: db_dependency):
    try:
        if current_user:
            get_con = await db.execute(select(LeafCondition))
            result = get_con.scalars().all()
            if not result :
                raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,
                                    detail = "leaf condition tidak ditemukan")
            return result
    except HTTPException as http_exc:
            # biarkan FastAPI tangani sesuai status code
            raise http_exc
    except SQLAlchemyError as db_err:
        print(f"DB error: {repr(db_err)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="kesalahan database"
        )

    except Exception as e:
        print(f"Detail error: {repr(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="terjadi kesalahan internal"
        )    

@leafcon.post("/add", status_code = status.HTTP_201_CREATED)
async def add_leaf_condition(admin: is_admin_depend,
                            db: db_dependency,
                            request: Request,
                            condition: str = Form(...),
                            description: str = Form(...),
                            treatment: str = Form(...),                            
                            
                            file: UploadFile = File(...) ):
    try: 
        if admin:
            image_path = image_saver(file, "condition")
            new_con = AddCondition(
                condition = condition,
                description = description,
                treatment = treatment,
                image_reference = image_path
            )
            smt = insert(LeafCondition).values(new_con.dict())
            await db.execute(smt)
            record = Log_Activity_Schema(
                                        action = "Menambahkan data kondisi daun",
                                        module = "leaf_condition_router",
                                        user_id = admin.id,
                                        email = admin.email,
                                        ip = get_ip(request),
                                        browser = get_browser(request)
                                    )
            await record_activity(
                db,
                record
            )
            await db.commit()
            return {"message": "success"}
    except Exception as e:
            print(f"Detail error: {repr(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="terjadi kesalahan internal"
            )

@leafcon.patch("/update/{id_leaf}", status_code = status.HTTP_200_OK)
async def update_leaf_condition(admin: is_admin_depend,
                                id_leaf: int,
                                db: db_dependency,
                                request: Request,
                                condition: str = Form(...),
                                description: str = Form(...),
                                treatment: str = Form(...),                     
                                file: UploadFile = File(...)):
    get_condition = await show_leaf_condition_detail(admin, db, id_leaf)
    try:
        
        if file is None:
            image_path = get_condition.image_reference
        image_delete(get_condition.image_reference)
        image_path = image_saver(file, "condition")
        update_con = Update_Leaf(
            condition = condition or get_condition,
            description = description or get_condition,
            treatment = treatment or get_condition,
            image_reference = image_path
        
        )
        smt = update(LeafCondition).where(LeafCondition.id == id_leaf).values(
            update_con.dict()
        )
        await db.execute(smt)
        record = Log_Activity_Schema(
                                    action = "Memperbaharui data kondisi daun",
                                    module = "leaf_condition_router",
                                    user_id = admin.id,
                                    email = admin.email,
                                    ip = get_ip(request),
                                    browser = get_browser(request)
                                )
        await record_activity(
            db,
            record
        )
        await db.commit()
        return {"message": "success"}
    except Exception as e:
        print(f"Detail error: {repr(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="terjadi kesalahan internal"
        )
@leafcon.delete("/delete/{id_leaf}", status_code=status.HTTP_200_OK)
async def delete_leaf_condition(admin: is_admin_depend,
                                id_leaf: int,
                                db: db_dependency,
                                request: Request):
    get_condition = await show_leaf_condition_detail(admin, db, id_leaf)
    try:
        
        image_delete(get_condition.image_reference)
        if admin:
            smt = delete(LeafCondition).where(LeafCondition.id == id_leaf)
            await db.execute(smt)
        record = Log_Activity_Schema(
            action = "Menghapus data kondisi daun",
            module = "leaf_condition_router",
            user_id = admin.id,
            email = admin.email,
            ip = get_ip(request),
            browser = get_browser(request)
        )
        await record_activity(
            db,
            record
        )
        await db.commit()
        return {"message": "success"}
    except Exception as e:
        print(f"Detail error: {repr(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="terjadi kesalahan internal"
        )

            

