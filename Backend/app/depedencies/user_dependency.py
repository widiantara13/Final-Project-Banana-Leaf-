from fastapi import HTTPException, Depends
from starlette import status
from sqlalchemy.future import select
from typing import Annotated
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from app.depedencies.db_dependency import db_dependency
from app.models.users_model import Users
import os
from  dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

seccret = os.getenv("SESS_TOKEN")
algoritma = os.getenv("HASH_ALGORITMA")

ouath_bearer = OAuth2PasswordBearer(tokenUrl="/auth/login")
token_dependency = Annotated[str, Depends(ouath_bearer)]






async def get_curent_user(token: token_dependency, db: db_dependency):
    
    try:
        payload = jwt.decode(token, seccret, algorithms=[algoritma])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                 detail="Tidak bisa memvalidasi kredensial",
                                 headers={"WWW-Authenticate": "Bearer"})
        user = await db.execute(select(Users).where(Users.email == email))
        return user.scalars().first()
        
    except JWTError as e:
        print(f"Detail error:{repr(e)}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                         detail="Tidak bisa memvalidasi kredensial 2",
                                         headers={"WWW-Authenticate": "Bearer"})
    
user_depend = Annotated[str, Depends(get_curent_user)]
form_data_dependency = Annotated[OAuth2PasswordRequestForm, Depends()]

async def is_admin(current_user: user_depend):
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Akses dilarang")
    return current_user
is_admin_depend = Annotated[str, Depends(is_admin)]