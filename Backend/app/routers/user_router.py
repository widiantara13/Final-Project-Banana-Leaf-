from fastapi import APIRouter, HTTPException
from starlette import status
from app.depedencies.user_dependency import is_admin_depend
from app.depedencies.db_dependency import db_dependency
from app.models.users_model import Users
from sqlalchemy.future import select



users = APIRouter(
    prefix = "/users",
    tags = ["users"],
    responses = {404: {"description": "not found"}}
)

@users.get("/show", status_code = status.HTTP_200_OK)
async def show_all_users(otoriti: is_admin_depend, db: db_dependency):
    try:
        if otoriti:
            get_users = await db.execute(select(Users))
            return get_users.scalars().all()
    except Exception as e:
        print(f"Detail error: {repr(e)}")
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail = f"terjadi kesalahan internal")

   


