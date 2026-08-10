from fastapi import FastAPI
from app.database.database import Base, engine
from app.models.leaf_conditon_model import LeafCondition
from app.models.log_activity_model import LogActivity
from app.models.models_model import Models
from app.models.predictions_model import Predictions
from app.models.profiles_model import Profiles
from app.models.users_model import Users


from fastapi import HTTPException
from starlette import status
from app.schemas.autentication_schema import Register
from app.depedencies.db_dependency import db_dependency

app = FastAPI()

Base.metadata.create_all(engine)

@app.get("/")
async def root():
    return {"message": "Hello, World!"}

@app.post("/auth/register/", status_code = status.HTTP_201_CREATED )
async def register_user(new_user: Register, db: db_dependency):
    db.add(Users(
        email = new_user.email,
        hashpassword = new_user.password))
            
        
    db.commit()
    return 1