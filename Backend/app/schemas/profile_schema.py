from pydantic import BaseModel
from typing import Optional


class IdUser(BaseModel):
    id: int

class UpdateDataProfile(BaseModel):
    full_name: Optional[str]=None
    address: Optional[str]=None
    phone_number: Optional[str]=None

class Profile(UpdateDataProfile):
    
    avatar: Optional[str]=None
    model_config = {
        "from_attributes": True
    }