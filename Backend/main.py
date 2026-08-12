from fastapi import FastAPI
from app.database.database import Base, engine
from app.models.leaf_conditon_model import LeafCondition
from app.models.log_activity_model import LogActivity
from app.models.models_model import Models
from app.models.predictions_model import Predictions
from app.models.profiles_model import Profiles
from app.models.users_model import Users
from app.routers.auth_routers import auth
from app.routers.test_router import tes
from fastapi import HTTPException
from starlette import status
from app.schemas.autentication_schema import Register
from app.depedencies.db_dependency import db_dependency

app = FastAPI()


@app.on_event("startup")
async def startup():
    async with engine.begin() as mulai:
        await mulai.run_sync(Base.metadata.create_all)

@app.get("/")
async def root():
    return {"message": "Hello, World!"}


app.include_router(auth)
app.include_router(tes)