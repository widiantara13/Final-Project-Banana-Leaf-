from fastapi import FastAPI, Depends
from app.database.database import Base, engine
from app.models.leaf_conditon_model import LeafCondition
from app.models.log_activity_model import LogActivity
from app.models.models_model import Models
from app.models.predictions_model import Predictions
from app.models.profiles_model import Profiles
from app.models.users_model import Users
from app.routers.auth_routers import auth
from app.routers.user_router import users
from app.routers.profiles_router import profile
from app.routers.log_activity_router import log
from app.routers.leaf_condition_router import leafcon
from app.routers.test_router import tes
from fastapi import HTTPException
from starlette import status
from fastapi.staticfiles import StaticFiles
from fastapi_pagination import add_pagination
from app.depedencies.user_dependency import ouath_bearer
from fastapi.openapi.utils import get_openapi


app = FastAPI()

add_pagination(app)
app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.mount("/ai", StaticFiles(directory="app/ai"), name="ai")

@app.on_event("startup")
async def startup():
    async with engine.begin() as mulai:
        await mulai.run_sync(Base.metadata.create_all)

@app.get("/me")
async def root(token: str = Depends(ouath_bearer)):
    return {"message": token}


app.include_router(auth)
app.include_router(users)
app.include_router(profile)
app.include_router(log)
app.include_router(leafcon)
app.include_router(tes)



# Include router kamu seperti biasa
# app.include_router(auth)

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="API Documentation",
        version="1.0.0",
        routes=app.routes,
    )
    
    # PAKSA ganti seluruh tokenUrl OAuth2 menjadi /auth/login
    for path, path_item in openapi_schema.get("components", {}).get("securitySchemes", {}).items():
        if path_item.get("type") == "oauth2":
            flows = path_item.get("flows", {})
            if "password" in flows:
                flows["password"]["tokenUrl"] = "/auth/login"
                
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi