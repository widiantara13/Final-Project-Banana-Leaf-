from pydantic import BaseModel


class ModelDP(BaseModel):
    id: int
    models_name: str
    model_type: str
    

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
    
    
