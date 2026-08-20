from app.schemas.model_schema import ModelDP, AddModel, Detail, TambahDM
from app.depedencies.db_dependency import db_dependency
from app.depedencies.user_dependency import is_admin_depend
from app.models.models_model import Models
from app.utils.log_activity_util import record_activity, get_browser, get_ip
from app.utils.models_utils import upload_model, set_active_all, start_up, update_set_model, set_inactive
from app.schemas.log_activity_schema import Log_Activity_Schema
from fastapi import APIRouter, Request, status, HTTPException, Form, File, UploadFile
from sqlalchemy.future import select
from sqlalchemy import insert, update, delete
from typing import List

model = APIRouter(
    prefix = "/model",
    tags = ["model"],
    responses = {404: {"description": "not found"}}

)

@model.post("/add", status_code = status.HTTP_201_CREATED)
async def add_model(admin: is_admin_depend,
                    db: db_dependency,
                    request: Request,
                    
                    model_type: str = Form(...),
                    class_model: int = Form(...),
                    
                    file: UploadFile = File(...)):
    try:
        if admin:
            upload = await upload_model(file)
            new_model = TambahDM(
                models_name = upload[0],
                model_type = model_type,
                class_model = class_model,
                id_owner = admin.id,
                url = upload[1]
            )
            smt = insert(Models).values(new_model.dict())
            await db.execute(smt)
            record = Log_Activity_Schema(
                action = "Menambahkan model baru",
                module = "model_router",
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
            print(f"Detail error: {repr(e)} disini erornya")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="terjadi kesalahan internal"
            )

@model.get("/show", response_model=List[ModelDP], status_code = status.HTTP_200_OK)
async def get_all_model(admin: is_admin_depend, db: db_dependency):
     try:
          if admin:
               get_models = await db.execute(select(Models))
               return get_models.scalars().all()
     except Exception as e:
          print(f"Detail error: {repr(e)}")
          raise HTTPException(
                          status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                          detail="terjadi kesalahan internal"
                      )

@model.get("/show/{id_model}", response_model=Detail, status_code = status.HTTP_200_OK)
async def get_detail_model(id_model: int, admin: is_admin_depend, db: db_dependency):
    try:
        if admin:
            get_a_model = await db.execute(select(Models).where(Models.id == id_model))
            return get_a_model.scalars().first()
    except Exception as e:
        print(f"Detail error: {repr(e)}")
        raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="terjadi kesalahan internal"
                    )
@model.get("/show-active", status_code = status.HTTP_200_OK)
async def get_active_model(admin: is_admin_depend, db: db_dependency):
    try:
        if admin:
            get_filter = await db.execute(select(Models).
                                where((Models.is_active == True) & 
                                (Models.model_type == False)))
            get_diseases = await db.execute(select(Models).
                                where((Models.is_active == True) &
                                (Models.model_type == True)))
            show_filter = get_filter.scalars().first()
            show_diseases = get_diseases.scalars().first()
            if show_filter is None and show_diseases is None:
                raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,
                                    detail = "Model tidak ditemukan")
            return [show_filter, show_diseases]
    except HTTPException:
        raise
    except Exception as e:
        print(f"Detail error: {repr(e)}")
        raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="terjadi kesalahan internal"
                    )
@model.get("/show-filter", response_model=List[ModelDP], status_code = status.HTTP_200_OK)
async def get_filter_model(admin: is_admin_depend, db: db_dependency):
    try:
        if admin:
            get_filter = await db.execute(select(Models).where(Models.model_type == False))
            mod = get_filter.scalars().all()
            if not mod:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                    detail = "Model tidak ditemukan")
            return mod
    except HTTPException:
        raise
    except Exception as e:
        print(f"Detail error: {repr(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail = "terjadi kesalahan internal")
    
@model.get("/show-diseases", response_model=List[ModelDP], status_code = status.HTTP_200_OK)
async def get_filter_model(admin: is_admin_depend, db: db_dependency):
    try:
        if admin:
            get_filter = await db.execute(select(Models).where(Models.model_type == True))
            mod = get_filter.scalars().all()
            if not mod :
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                    detail = "Model tidak ditemukan")
            return mod
    except HTTPException:
        raise
    except Exception as e:
        print(f"Detail error: {repr(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail = "terjadi kesalahan internal")

@model.post("/set-active", status_code = status.HTTP_200_OK)
async def set_active_model(admin: is_admin_depend, db: db_dependency,
                            request: Request,id_dieases: int = Form(...), id_filter: int = Form(...)):
    try:
        if admin:
            get_filter = await db.execute(select(Models).where(Models.id == id_filter))
            get_diseases = await db.execute(select(Models).where(Models.id == id_dieases))
            filter = get_filter.scalars().first()
            diseases = get_diseases.scalars().first()
            if filter.model_type == diseases.model_type:
                raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST,
                                    detail = "Harus memilih tipe model yang sesuai")
            set_active = await set_active_all(filter.url, diseases.url)
            status_filter =  update(Models).where(Models.id == id_filter).values(
                is_active = set_active
            
            )
            status_diseases =  update(Models).where(Models.id == id_dieases).values(
                is_active = set_active
            )
            await db.execute(status_filter)
            await db.execute(status_diseases)
            record = Log_Activity_Schema(
                            action = "Mengaktifkan kedua model",
                            module = "model_router",
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
            return {"detail": "success"}
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        print(f"Detail error: {repr(e)}")
        raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="terjadi kesalahan internal")

async def set_status_automatic():
    try:
        return await start_up()
    except Exception as e:
        print(f"Detail error: {repr(e)}")




@model.put("/set-status/{id_model}", status_code=status.HTTP_200_OK)
async def set_model(id_model: int, admin: is_admin_depend, db: db_dependency, request: Request):
    try:
        if admin:
        #Mengambil data model berdasarkan id
            get_model = await get_detail_model(id_model, admin, db)
            url = get_model.url
            id_new_model = get_model.id
            stats = get_model.is_active
            name = get_model.models_name
            type_mod = get_model.model_type

        #mengambil data model yang ingin digantikan
            get_current_model = await db.execute(select(Models).
                                where(Models.is_active == True and 
                                Models.model_type == type_mod))
            id_current_model = get_current_model.scalars().first().id

        #memperbaharui record data kedua model
            new_model = update(Models).where(Models.id == id_new_model).values(
                is_active = True)
            current_model = update(Models).where(Models.id == id_current_model).values(
                is_active = False)
        
            
            await db.execute(new_model)
            await db.execute(current_model)
            await db.flush()
            get_active = await get_active_model(admin, db)
            filter = get_active[0].url
            diseases = get_active[1].url
            await update_set_model(filter, diseases)
        
        record = Log_Activity_Schema(
            action = f"Mengaktifkan {name}",
            module = "model_router",
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
                        detail="terjadi kesalahan internal")


@model.post("/deactivate-all", status_code = status.HTTP_200_OK)
async def deactivate_all(admin: is_admin_depend, db: db_dependency, request: Request):
    try:
        if admin:
            get_active = await get_active_model(admin, db)
            filter = get_active[0].id
            diseases = get_active[1].id
            filter_model = update(Models).where(Models.id == filter).values(
                            is_active = False)
            diseases_model = update(Models).where(Models.id == diseases).values(
                is_active = False)
            await db.execute(filter_model)
            await db.execute(diseases_model)
            await set_inactive()
            record = Log_Activity_Schema(
                        action = f"Menonaktifkan semua model",
                        module = "model_router",
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
            return {"detail": "success"}
    except Exception as e:
        print(f"Detail error: {repr(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail = "terjadi kesalahan internal")
            




@model.delete("/delete/{id_model}", status_code = status.HTTP_200_OK)
async def delete_model(admin: is_admin_depend, id_model: int, db: db_dependency, request: Request):
    try:
        if admin:
            get_model = await get_detail_model(id_model, admin, db)
            if get_model.is_active == True:
                raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST,
                                    detail = "Model masih aktif")
            await db.execute(delete(Models).where(Models.id == id_model))
        record = Log_Activity_Schema(
                    action = f"Menghapus model{get_model.models_name}",
                    module = "model_router",
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
        return {"message": f"berhasil menghapus model{get_model.models_name}"}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Detail error: {repr(e)}")
        raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="terjadi kesalahan internal")
    

        
        

             