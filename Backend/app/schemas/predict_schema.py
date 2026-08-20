from pydantic import BaseModel
from datetime import datetime

class History(BaseModel):
    id: int
    image_path: str
    condition: str
    confidence: float

class DoPredict(BaseModel):
    owner_id: int
    image_path: str
    leaf_condition_id: int
    
    confidence: float

class Detail(History):
    uuid: str
    owner_id: int
    created_at: datetime
