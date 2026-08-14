from fastapi import APIRouter, HTTPException, Request, File, UploadFile
from starlette import status
from app.depedencies.user_dependency import is_admin_depend, user_depend
from app.depedencies.db_dependency import db_dependency
from app.models.users_model import Users
from app.models.profiles_model import Profiles
from app.schemas.profile_schema import Profile, UpdateDataProfile
from app.utils.log_activity_util import record_activity, get_ip, get_browser
from app.schemas.log_activity_schema import Log_Activity_Schema
from app.utils.image_utils import image_saver, image_delete
from sqlalchemy.future import select
from sqlalchemy import update






profile = APIRouter(
    prefix = "/profile",
    tags = ["profile"],
    responses = {404: {"description": "not found"}}
)


@profile.get("/show", response_model = Profile, status_code = status.HTTP_200_OK)
async def get_profile(current_user: user_depend, db: db_dependency):
    try:
        user = await db.execute(select(Profiles).where(Profiles.user_id == current_user.id))
        return user.scalars().first()
    except Exception as e:
        print(f"Detail error: {repr(e)}")
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail = f"terjadi kesalahan internal")

@profile.get("/show/{id_user}",response_model = Profile, status_code = status.HTTP_200_OK)
async def get_user_profile(id_user: int, otoriti: is_admin_depend, db: db_dependency):
    try:
        if otoriti:
            user = await db.execute(select(Profiles).where(Profiles.user_id == id_user))
            return user.scalars().first()
    except Exception as e:
        print(f"Detail error: {repr(e)}")
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail = f"terjadi kesalahan internal")

@profile.put("/update-image", status_code=status.HTTP_200_OK)
async def update_image_profile(db:db_dependency, current_user: user_depend, request: Request, file: UploadFile = File(...)):
    prof = await get_profile(current_user, db)
    if prof.avatar == "app/static/profile_images/avatar/avatar_img.jpg":               
        image_path = image_saver(file, "profile_images")
    image_delete(prof.avatar)
    image_path = image_saver(file, "profile_images")
    
    try:
        update_image = update(Profiles).where(Profiles.user_id == current_user.id).values(
            avatar = image_path
        )
        record = Log_Activity_Schema(
                            action = "Update Gambar Profile",
                            module = "profiles_router",
                            user_id = current_user.id,
                            email = current_user.email,
                            ip = get_ip(request),
                            browser = get_browser(request)
                        )
        await record_activity(
            db,
            record
        )
        await db.execute(update_image)
        await db.commit()
        return {"msg": "berhasil update gambar profile"}
    except Exception as e:
        print(f"Detail error: {repr(e)}")
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
                                    detail = f"terjadi kesalahan internal")

@profile.patch("/update", status_code = status.HTTP_200_OK)
async def update_data_profile( db: db_dependency, current_user: user_depend, profile: UpdateDataProfile, request: Request):
    prof = await get_profile(current_user, db)
    
    try:
        
        update_prof =  update(Profiles).where(Profiles.user_id == current_user.id).values(
            full_name = profile.full_name or prof.full_name,
            address = profile.address or prof.address,
            phone_number = profile.phone_number or prof.phone_number,
            
        )
        record = Log_Activity_Schema(
                    action = "Update Data Profile",
                    module = "profiles_router",
                    user_id = current_user.id,
                    email = current_user.email,
                    ip = get_ip(request),
                    browser = get_browser(request)
                )
        await record_activity(
            db,
            record
        )
        await db.execute(update_prof)
        await db.commit()
        return {"msg": "berhasil update data profile"}
    except Exception as e:
        print(f"Detail error: {repr(e)}")
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
                                    detail = f"terjadi kesalahan internal")

@profile.delete("/delete", status_code = status.HTTP_200_OK)
async def delete_profile(db: db_dependency, current_user: user_depend, request: Request):
    prof = await get_profile(current_user, db)
    image_delete(prof.avatar)               
    try:
        update_image = update(Profiles).where(Profiles.user_id == current_user.id).values(
            
            avatar = "app/static/profile_images/avatar/avatar_img.jpg"
        )
        record = Log_Activity_Schema(
                            action = "Hapus Gambar Profile",
                            module = "profiles_router",
                            user_id = current_user.id,
                            email = current_user.email,
                            ip = get_ip(request),
                            browser = get_browser(request)
                        )
        await record_activity(
            db,
            record
        )
        await db.execute(update_image)
        await db.commit()
        return {"msg": "berhasil hapus gambar profile"}
    except Exception as e:
        print(f"Detail error: {repr(e)}")
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
                                    detail = f"terjadi kesalahan internal")
