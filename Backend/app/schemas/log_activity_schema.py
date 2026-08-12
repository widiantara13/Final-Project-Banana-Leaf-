from pydantic import BaseModel
from typing import Optional



class Log_Activity_Schema(BaseModel):
    action: str
    module: str
    user_id: Optional[int]
    email: Optional[str]
    ip: Optional[str]
    browser: Optional[str]
    
    model_config = {
        "from_atributes" : True
    }