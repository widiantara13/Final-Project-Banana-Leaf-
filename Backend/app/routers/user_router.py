from fastapi import APIRouter, HTTPException
from starlette import status
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from app.depedencies.user_dependency import is_admin_depend
from app.depedencies.db_dependency import db_dependency
from app.models.users_model import Users
from app.schemas.user_schema import UserResponse
from sqlalchemy.future import select


users = APIRouter(
    prefix = "/users",
    tags = ["users"],
    responses = {404: {"description": "not found"}}
)

@users.get("/show", response_model=Page[UserResponse], status_code = status.HTTP_200_OK)
async def show_all_users(otoriti: is_admin_depend, db: db_dependency) -> Page[UserResponse]:
    try:
        if otoriti:
            query = select(Users).order_by(Users.id.asc())
            return await paginate(db, query)
    except Exception as e:
        print(f"Detail error: {repr(e)}")
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail = f"terjadi kesalahan internal")

   


