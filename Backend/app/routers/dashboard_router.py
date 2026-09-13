from fastapi import APIRouter, HTTPException, status, Request, Query, Depends
from starlette.responses import StreamingResponse
from sqlalchemy.future import select
from sqlalchemy import func
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import asyncio
import json
import os
from jose import jwt, JWTError
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())
seccret = os.getenv("SESS_TOKEN")
algoritma = os.getenv("HASH_ALGORITMA")

from app.depedencies.db_dependency import db_dependency
from app.depedencies.user_dependency import is_admin_depend
from app.models.users_model import Users
from app.models.profiles_model import Profiles
from app.models.predictions_model import Predictions
from app.models.leaf_conditon_model import LeafCondition
from app.models.log_activity_model import LogActivity

dashboard = APIRouter(
    prefix="/dashboard",
    tags=["dashboard"],
    responses={404: {"description": "not found"}}
)

@dashboard.get("/summary", status_code=status.HTTP_200_OK)
async def get_dashboard_summary(admin: is_admin_depend, db: db_dependency) -> Dict[str, Any]:
    try:
        if not admin:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

        # 1. Baris 1: Total Users, Active Users, Total Predictions
        total_users_res = await db.scalar(select(func.count(Users.id))) or 0
        active_users_res = await db.scalar(
            select(func.count(Users.id)).where(Users.is_active == True)
        ) or 0
        total_predictions_res = await db.scalar(select(func.count(Predictions.id))) or 0

        # 2. Baris 2: Kondisi Daun (Sigatoka, Cordana, Healthy, Panama)
        con_counts_query = await db.execute(
            select(Predictions.leaf_condition_id, func.count(Predictions.id))
            .group_by(Predictions.leaf_condition_id)
        )
        con_counts_dict = {row[0]: row[1] for row in con_counts_query.all()}

        leaf_conditions_query = await db.execute(select(LeafCondition).order_by(LeafCondition.id.asc()))
        all_leaf_conditions = leaf_conditions_query.scalars().all()

        conditions_summary = []
        named_conditions: Dict[str, int] = {
            "sigatoka": 0,
            "cordana": 0,
            "healthy": 0,
            "panama": 0,
        }

        for lc in all_leaf_conditions:
            cnt = con_counts_dict.get(lc.id, 0)
            conditions_summary.append({
                "id": lc.id,
                "name": lc.condition,
                "count": cnt,
            })
            c_lower = lc.condition.lower()
            if "sigatoka" in c_lower or "sigota" in c_lower:
                named_conditions["sigatoka"] += cnt
            elif "cordana" in c_lower:
                named_conditions["cordana"] += cnt
            elif "health" in c_lower or "sehat" in c_lower:
                named_conditions["healthy"] += cnt
            elif "panama" in c_lower:
                named_conditions["panama"] += cnt

        # 3. Baris 3: Tren Prediksi 7 Hari Terakhir
        today = datetime.now().date()
        days_names_id = ["Sen", "Sel", "Rab", "Kam", "Jum", "Sab", "Min"]
        seven_days_ago = datetime.combine(today - timedelta(days=6), datetime.min.time())

        trends_query = await db.execute(
            select(func.date(Predictions.created_at).label("pred_date"), func.count(Predictions.id))
            .where(Predictions.created_at >= seven_days_ago)
            .group_by(func.date(Predictions.created_at))
        )
        trends_map = {str(row[0]): row[1] for row in trends_query.all()}

        prediction_trends = []
        for i in range(6, -1, -1):
            d = today - timedelta(days=i)
            d_str = d.strftime("%Y-%m-%d")
            day_name = days_names_id[d.weekday()]
            prediction_trends.append({
                "date": d_str,
                "label": f"{day_name}, {d.strftime('%d/%m')}",
                "day": day_name,
                "count": trends_map.get(d_str, 0)
            })

        # 4. Baris 3 Kanan: Data User Aktif Terbaru (Maksimal 5)
        users_query = await db.execute(
            select(Users, Profiles)
            .outerjoin(Profiles, Users.id == Profiles.user_id)
            .where(Users.is_active == True)
            .order_by(Users.created_at.desc())
            .limit(5)
        )
        active_users_list = []
        for u, p in users_query.all():
            active_users_list.append({
                "id": u.id,
                "email": u.email,
                "role": u.role.value if hasattr(u.role, "value") else str(u.role),
                "is_active": u.is_active,
                "full_name": p.full_name if p and p.full_name else u.email.split("@")[0],
                "avatar": p.avatar if p else None,
                "created_at": u.created_at.isoformat() if u.created_at else None,
            })

        # 5. Baris 4 Kiri: Log Aktivitas Terbaru (Maksimal 5)
        logs_query = await db.execute(
            select(LogActivity)
            .order_by(LogActivity.created_at.desc())
            .limit(5)
        )
        recent_logs = []
        for l in logs_query.scalars().all():
            recent_logs.append({
                "id": l.id,
                "action": l.action,
                "module": l.module,
                "email": l.email,
                "ip": l.ip,
                "browser": l.browser,
                "created_at": l.created_at.isoformat() if l.created_at else None,
            })

        # 6. Baris 4 Kanan: Riwayat Prediksi Terbaru (Maksimal 5)
        preds_query = await db.execute(
            select(
                Predictions.id,
                Predictions.image_path,
                Predictions.confidence,
                Predictions.created_at,
                LeafCondition.condition.label("condition_name"),
                Users.email.label("user_email")
            )
            .join(LeafCondition, Predictions.leaf_condition_id == LeafCondition.id)
            .join(Users, Predictions.owner_id == Users.id)
            .order_by(Predictions.created_at.desc())
            .limit(5)
        )
        recent_predictions = []
        for row in preds_query.all():
            recent_predictions.append({
                "id": row.id,
                "image_path": row.image_path,
                "confidence": round(row.confidence, 1) if row.confidence is not None else 0.0,
                "condition": row.condition_name,
                "email": row.user_email,
                "created_at": row.created_at.isoformat() if row.created_at else None,
            })

        return {
            "total_users": total_users_res,
            "active_users": active_users_res,
            "total_predictions": total_predictions_res,
            "conditions_count": named_conditions,
            "conditions_list": conditions_summary,
            "prediction_trends": prediction_trends,
            "active_users_list": active_users_list,
            "recent_logs": recent_logs,
            "recent_predictions": recent_predictions,
        }

    except Exception as e:
        print(f"Detail error dashboard: {repr(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Terjadi kesalahan saat memuat data dashboard"
        )


from app.utils.sse_manager import dashboard_broadcaster

async def get_admin_for_sse(
    db: db_dependency,
    token: Optional[str] = Query(None),
    request: Request = None,
):
    # Ambil token baik dari Query param ?token=... maupun dari Header Authorization
    auth_token = token
    if not auth_token and request:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            auth_token = auth_header.split(" ")[1]

    if not auth_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Autentikasi diperlukan untuk stream dashboard"
        )

    try:
        payload = jwt.decode(auth_token, seccret, algorithms=[algoritma])
        email: str = payload.get("sub")
        if not email:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token tidak valid")

        user_query = await db.execute(select(Users).where(Users.email == email))
        user = user_query.scalars().first()
        if not user or user.role != "admin":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Akses ditolak")
        return user
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token tidak valid atau telah kedaluwarsa")


@dashboard.get("/stream")
async def dashboard_sse_stream(
    request: Request,
    admin: Any = Depends(get_admin_for_sse)
):
    """
    Endpoint SSE (Server-Sent Events) untuk streaming event real-time ke admin dashboard.
    Koneksi akan tetap terbuka dan mengirim update setiap kali ada aktivitas baru di sistem.
    """
    queue = await dashboard_broadcaster.connect()

    async def event_generator():
        # Kirim sinyal konfirmasi awal koneksi berhasil
        yield f"data: {json.dumps({'type': 'CONNECTED', 'message': 'SSE Connected to Dashboard'})}\n\n"
        try:
            while True:
                # Periksa apakah browser admin sudah menutup halaman/tab
                if await request.is_disconnected():
                    break
                try:
                    # Tunggu pesan event baru dengan timeout 25 detik (heartbeat ping)
                    message = await asyncio.wait_for(queue.get(), timeout=25.0)
                    yield message
                except asyncio.TimeoutError:
                    # Kirim SSE comment ping agar koneksi tidak diputus oleh browser/proxy
                    yield ": ping\n\n"
        finally:
            dashboard_broadcaster.disconnect(queue)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )

