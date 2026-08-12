# Mengimport pustaka yang diperlukan
from fastapi import APIRouter, HTTPException, Request, Depends
from starlette import status
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from sqlalchemy.future import select
from sqlalchemy import insert
from datetime import timedelta
from app.schemas.autentication_schema import Register, Autentication, Email
from app.schemas.log_activity_schema import Log_Activity_Schema as record_schema
from app.depedencies.db_dependency import db_dependency
from app.depedencies.user_dependency import form_data_dependency, user_depend
from app.models.users_model import Users
from app.models.profiles_model import Profiles
from app.utils.log_activity_util import record_activity, get_ip, get_browser
from app.schemas.create_token_schema import Token
from app.utils.create_token import create_access_token
from typing import Annotated

auth = APIRouter(
    prefix = "/auth",
    tags = ["authentication"],
    responses = {404: {"description": "Not found"}}
)

ph = PasswordHasher()


async def existing_user(email_need: Email, db_need):
    get_user = await db_need.execute(select(Users).where(Users.email == email_need))
    
    return  get_user.scalars().first()


@auth.post("/register/", status_code = status.HTTP_201_CREATED)
async def register_user(register: Register, db: db_dependency, request: Request):
    #Cek apakah email sudah terdapftar apa belum
    is_exist = await existing_user(register.email, db)
    if is_exist:
        raise HTTPException(status_code = status.HTTP_409_CONFLICT, detail = "Email sudah terdaftar")

    #Hash password
    hashed_password = ph.hash(register.password)
    new_user = Users(
        email = register.email,
        hashpassword = hashed_password
    )
    try:
        db.add(new_user)
        await db.flush()
        new_profile = insert(Profiles).values(
            user_id = new_user.id
        )
        await db.execute(new_profile)
        
        
        record = record_schema(
            action = "Register",
            module = "auth_router",
            user_id = new_user.id,
            email = new_user.email,
            ip = get_ip(request),
            browser = get_browser(request)
        )
        await record_activity(
            db,
            record
        )
        await db.commit()
        await db.refresh(new_user)
        return {"message": f"{new_user.email} berhasil melakukan register"}
    except Exception as e:
        await db.rollback()
        print(f"Detail error: {repr(e)}")
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail = f"terjadi kesalahan internal")

@auth.post("/login", status_code = status.HTTP_200_OK)
async def login_user(form_data: form_data_dependency, db: db_dependency, request: Request):
    #Cek apakah email sudah terdaftar
    user = await existing_user(form_data.username, db)
    print(user)
    if not user:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "Email tidak terdaftar")
    try:
        ph.verify(user.hashpassword, form_data.password)
    except VerifyMismatchError:
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail = "Password salah")

    token = Token(
        email = user.email,
        uuid = user.uuid,
        expire_delta = timedelta(minutes = 30)
    )
    
    access_token = create_access_token(token)
    
    try:
                        
            record = record_schema(
                action = "login",
                module = "auth_router",
                user_id = user.id,
                email = user.email,
                ip = get_ip(request),
                browser = get_browser(request)
            )
            await record_activity(
                db,
                record
            )         
            
    except Exception as e:
        await db.rollback()
        print(f"Detail error: {repr(e)}")
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail = f"terjadi kesalahan internal")
    return {"access_token": access_token, "token_type": "bearer"}

@auth.post("/logout/", status_code=status.HTTP_200_OK)
async def log_out(db: db_dependency, current_user: user_depend, request: Request):
    
    
        
    record = record_schema(
                    action = "logout",
                    module = "auth_router",
                    user_id = current_user.id,
                    email = current_user.email,
                    ip = get_ip(request),
                    browser = get_browser(request)
                )
    await record_activity(
        db,
        record
    ) 
    return {"status": "success", "message": "Berhasil logout"} 
    

