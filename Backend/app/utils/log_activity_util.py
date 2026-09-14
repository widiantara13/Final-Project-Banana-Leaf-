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

def get_browser(request: Request) -> str:
    raw_ua = request.headers.get("User-Agent", "").strip()
    if not raw_ua:
        return "Unknown/1.0/Unknown/Desktop"

    # Deteksi jika request berasal dari Aplikasi Mobile BananaLeaf
    if "BananaLeaf-Mobile" in raw_ua:
        os_name = "Android" if "Android" in raw_ua else ("iOS" if "iOS" in raw_ua else "Mobile")
        return f"BananaLeaf-App/1.0/{os_name}/Mobile"

    # Fallback jika aplikasi Flutter mengirim User-Agent default bawaan Dart
    if "Dart/" in raw_ua:
        return "BananaLeaf-App/Flutter/Android/Mobile"

    # Parsing untuk Web Browser standar (Chrome, Firefox, Safari, Edge, dll.)
    try:
        user_agent = parse(raw_ua)
        user_browser = user_agent.browser.family
        user_browser_version = user_agent.browser.version_string or "1.0"
        user_os = user_agent.os.family
        is_mobile = user_agent.is_mobile or "Mobile" in raw_ua
        device = "Mobile" if is_mobile else "Desktop"

        if user_browser == "Other" and is_mobile:
            user_browser = "Mobile App"

        return f"{user_browser}/{user_browser_version}/{user_os}/{device}"
    except Exception:
        return "Browser/1.0/Other/Desktop"


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

        # Siarkan event live SSE ke dashboard admin yang sedang terhubung
        try:
            from app.utils.sse_manager import dashboard_broadcaster
            await dashboard_broadcaster.broadcast({
                "type": "NEW_ACTIVITY",
                "action": record.action,
                "module": record.module,
                "email": record.email,
            })
        except Exception as sse_err:
            print(f"[SSE Broadcast Warning]: {repr(sse_err)}")

    except Exception as e:
        db.rollback()
        print(f"Detail error: {repr(e)}")
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail = f"terjadi kesalahan internal")