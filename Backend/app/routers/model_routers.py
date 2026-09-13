from app.schemas.model_schema import ModelDP, AddModel, Detail, TambahDM
from app.depedencies.db_dependency import db_dependency
from app.depedencies.user_dependency import is_admin_depend
from app.models.models_model import Models
from app.utils.log_activity_util import record_activity, get_browser, get_ip
from app.schemas.log_activity_schema import Log_Activity_Schema
from app.utils.models_utils import (
    upload_model,
    set_active_all,
    start_up,
    update_set_model,
    set_inactive,
    load_model_filter,
    load_model_diseases,
    unload_model_filter,
    unload_model_diseases,
    resolve_model_path,
    is_filter_type,
    is_disease_type,
    FILTER_TYPES,
    DISEASE_TYPES,
)
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
            get_filter = await db.execute(
                select(Models).where(
                    (Models.is_active == True)
                    & (Models.model_type.in_(["0", "False", "false", "Filter", "filter"]))
                )
            )
            get_diseases = await db.execute(
                select(Models).where(
                    (Models.is_active == True)
                    & (Models.model_type.in_(["1", "True", "true", "Prediksi", "diseases", "dieases"]))
                )
            )
            show_filter = get_filter.scalars().first()
            show_diseases = get_diseases.scalars().first()
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
            # 1. Mengambil data model berdasarkan id
            get_model = await get_detail_model(id_model, admin, db)
            if not get_model:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Model tidak ditemukan")

            url = get_model.url
            id_new_model = get_model.id
            name = get_model.models_name
            type_mod = get_model.model_type

            # Tentukan kelompok tipe model
            is_filter = is_filter_type(type_mod)
            target_types = FILTER_TYPES if is_filter else DISEASE_TYPES

            # 2. Menonaktifkan model aktif lama yang bertipe sama (aman jika belum ada)
            await db.execute(
                update(Models)
                .where((Models.is_active == True) & (Models.model_type.in_(target_types)))
                .values(is_active=False)
            )

            # 3. Mengaktifkan model baru di database
            await db.execute(
                update(Models).where(Models.id == id_new_model).values(is_active=True)
            )

            # 4. Muat model baru ke memori TensorFlow Keras secara independen (hot-swap)
            resolved_url = resolve_model_path(url)
            if is_filter:
                await load_model_filter(resolved_url)
            else:
                await load_model_diseases(resolved_url)

            # 5. Catat log aktivitas admin
            record = Log_Activity_Schema(
                action=f"Mengaktifkan {name}",
                module="model_router",
                user_id=admin.id,
                email=admin.email,
                ip=get_ip(request),
                browser=get_browser(request)
            )
            await record_activity(db, record)
            await db.commit()
            return {"message": "success", "detail": f"Model {name} berhasil diaktifkan"}
    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        print(f"Detail error: {repr(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="terjadi kesalahan internal saat mengaktifkan model"
        )


@model.put("/deactivate/{id_model}", status_code=status.HTTP_200_OK)
async def deactivate_model(id_model: int, admin: is_admin_depend, db: db_dependency, request: Request):
    try:
        if admin:
            get_model = await get_detail_model(id_model, admin, db)
            if not get_model:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Model tidak ditemukan")

            name = get_model.models_name
            type_mod = get_model.model_type

            # Jika model memang sudah tidak aktif
            if not get_model.is_active:
                return {"message": "success", "detail": f"Model {name} sudah dalam keadaan nonaktif"}

            # Update status di database menjadi nonaktif
            await db.execute(
                update(Models).where(Models.id == id_model).values(is_active=False)
            )

            # Kosongkan dari memori Keras sesuai tipenya
            if is_filter_type(type_mod):
                await unload_model_filter()
            else:
                await unload_model_diseases()

            record = Log_Activity_Schema(
                action=f"Menonaktifkan {name}",
                module="model_router",
                user_id=admin.id,
                email=admin.email,
                ip=get_ip(request),
                browser=get_browser(request)
            )
            await record_activity(db, record)
            await db.commit()
            return {"message": "success", "detail": f"Model {name} berhasil dinonaktifkan"}
    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        print(f"Detail error: {repr(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="terjadi kesalahan internal saat menonaktifkan model"
        )


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
    

        
        

             