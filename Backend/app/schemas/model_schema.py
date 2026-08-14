from pydantic import BaseModel


class ModelDP(BaseModel):
    id: int
    id_owner: int
    models_name: str
    model_type: str
    
    
