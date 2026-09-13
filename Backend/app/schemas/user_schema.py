from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.models.users_model import UserRole

class UserResponse(BaseModel):
    id: int
    uuid: str
    email: str
    role: UserRole
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }

