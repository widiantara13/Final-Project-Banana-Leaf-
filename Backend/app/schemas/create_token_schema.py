from pydantic import BaseModel
from datetime import timedelta


class Token(BaseModel):
    email: str
    uuid:str
    expire_delta: timedelta