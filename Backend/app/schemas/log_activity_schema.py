from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class Log_Individu(BaseModel):
    id: int
    user_id: Optional[int]
    email: Optional[str]
    action: str
    created_at: datetime

class Detail_Log(Log_Individu):
    module: str   
    
    ip: Optional[str]
    browser: Optional[str]
class Log_Activity_Schema(BaseModel):
    email: Optional[str]
    action: str
    module: str
    user_id: Optional[int]
    email: Optional[str]
    ip: Optional[str]
    browser: Optional[str]
    
    model_config = {
        "from_atributes" : True
    }