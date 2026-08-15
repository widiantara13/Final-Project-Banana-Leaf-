from pydantic import BaseModel
from typing import Optional

class Leaf_Condition(BaseModel):
    condition : str
    image_reference : str

class AddCondition(Leaf_Condition):
    description: str
    treatment: str

class Detail_Leaf(AddCondition):
    id: int

class Update_Leaf(BaseModel):
    condition: Optional[str]
    description: Optional[str]
    treatment: Optional[str]
    image_reference: Optional[str]