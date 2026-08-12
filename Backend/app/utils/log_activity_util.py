from app.depedencies.db_dependency import db_dependency
from app.models.log_activity_model import LogActivity
from app.schemas.log_activity_schema import Log_Activity_Schema
from fastapi import HTTPException, Request
from starlette import status
from user_agents import parse
from sqlalchemy import insert
import os


def get_ip(request: Request):
    return request.client.host

def get_browser(request: Request):
    user_agent = parse(request.headers["User-Agent"])
    user_browser = user_agent.browser.family
    user_browser_version = user_agent.browser.version_string
    user_os = user_agent.os.family
    is_mobile = user_agent.is_mobile
    device: bool = "Mobile" if is_mobile else "Desktop"
    return f"{user_browser}/{user_browser_version}/{user_os}/{device}"


async def record_activity(db: db_dependency, record: Log_Activity_Schema):
    
        
    new_activity = insert(LogActivity).values(
        action = record.action,
        module = record.module,
        user_id = record.user_id,
        email = record.email,
        ip = record.ip,
        browser = record.browser)

    try:
        await db.execute(new_activity)
        await db.commit()
    except Exception as e:
        db.rollback()
        print(f"Detail error: {repr(e)}")
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail = f"terjadi kesalahan internal")