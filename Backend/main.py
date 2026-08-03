from fastapi import FastAPI
from app.database.database import Base, engine
from app.models.leaf_conditon_model import LeafCondition
from app.models.log_activity_model import LogActivity
from app.models.models_model import Models
from app.models.predictions_model import Predictions
from app.models.profiles_model import Profiles
from app.models.users_model import Users

app = FastAPI()

Base.metadata.create_all(engine)

@app.get("/")
async def root():
    return {"message": "Hello, World!"}
