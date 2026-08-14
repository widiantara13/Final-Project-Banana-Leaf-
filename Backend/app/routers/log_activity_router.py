from app.models.log_activity_model import LogActivity
from app.schemas.log_activity_schema import Log_Individu
from app.depedencies.db_dependency import db_dependency
from app.depedencies.user_dependency import is_admin_depend
from fastapi import HTTPException, APIRouter
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from starlette import status
from sqlalchemy.future import select



log = APIRouter(
    prefix = "/log",
    tags = ["log"],
    responses = {404: {"description": "not found"}}
)

@log.get("/show", status_code = status.HTTP_200_OK)
async def show_log(otoriti: is_admin_depend, db: db_dependency)->Page[Log_Individu]:
    try:
        if otoriti:
            query = select(LogActivity).order_by(LogActivity.created_at.asc())
            return await paginate(db, query)
    except Exception as e:
        print(f"Detail error: {repr(e)}")
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail = f"terjadi kesalahan internal")

@log.get("/show/{id_user}", status_code = status.HTTP_200_OK)
async def show_log_a_user(id_user: int, otoriti: is_admin_depend, db: db_dependency)->Page[Log_Individu]:
    try:
        if otoriti:
            query = select(LogActivity).where(LogActivity.user_id == id_user).order_by(LogActivity.created_at.asc())
            return await paginate(db, query)
    except Exception as e:
        print(f"Detail error: {repr(e)}")
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail = f"terjadi kesalahan internal")
     
@log.get("show/{id_user}/{id_log}", status_code = status.HTTP_200_OK)
async def show_log_user_detail(id_user: int, id_log: int, otoriti: is_admin_depend, db: db_dependency):
    try:
        if otoriti:
            get_log = await db.execute(select(LogActivity).where(LogActivity.user_id == id_user).
                                       where(LogActivity.id == id_log))
            return get_log.scalars().first()
    except Exception as e:
            print(f"Detail error: {repr(e)}")
            raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail = f"terjadi kesalahan internal")