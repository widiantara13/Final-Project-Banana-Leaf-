# Menginport pustaka yang diperlukan dalam skema
from pydantic import (
    BaseModel,
    EmailStr,
    Field,
    model_validator
)
class Email(BaseModel):
    email: EmailStr = Field(min_length = 8, max_length = 40)
#Schema autentiksasi
class Autentication (Email):
    password: str = Field(min_length = 8, max_length = 60)

#Schema register
class Register (Autentication):
    confirm_password : str = Field(min_length = 8, max_length = 60)
    @model_validator(mode = "after")
    def validate_password (self) -> "Register":
        pw = self.password
        cp = self.confirm_password
        if pw != cp:
            raise ValueError("Password tidak sama")
        return self
    model_config = {
        "from_atribut": True
    }
