from fastapi import HTTPException, Depends
from starlette import status
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

ouath_bearer = OAuth2PasswordBearer(tokenUrl = "/auth/login")
Token = Annotated[str, Depends(ouath_bearer)]
# def get_user(token: Token,db: db_dependency):



form_data_dependency = Annotated[OAuth2PasswordRequestForm, Depends()]

