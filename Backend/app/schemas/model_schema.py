from pydantic import BaseModel
from typing import Optional

class ModelDP(BaseModel):
    id: int
    models_name: str
    model_type: str
    is_active: bool = False
    class_model: Optional[int] = None
    url: Optional[str] = None

    model_config = {
        "from_attributes": True
    }

class AddModel(ModelDP):
    class_model: int
    id_owner: int
    url: str

class TambahDM(BaseModel):
    class_model: int
    id_owner: int
    url: str
    models_name: str
    model_type: str

class Detail(AddModel):
    is_active: bool

    model_config = {
        "from_attributes": True
    }
