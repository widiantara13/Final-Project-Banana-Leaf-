# Menginport pustaka yang dibutuhkan dalam model
from app.database.database import Base
from sqlalchemy import (
    BigInteger, 
    String,
    DateTime,
    ForeignKey)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship)
from sqlalchemy.sql import func
from datetime import datetime

# Membuat class LogActivity untuk mendefinisikan model seluruh log aktivitas pengguna
class LogActivity(Base):
    __tablename__ = "log_activity" # Nama entitas tabel dalam basis data
    id : Mapped[int] = mapped_column(
        BigInteger,
        primary_key = True,
        index = True,
        autoincrement = True)
    action: Mapped[str] = mapped_column(
        String(150),
        nullable = False
    )
    module: Mapped[str] = mapped_column(
        String(30),
        nullable = False
    )
    created_at : Mapped[datetime] = mapped_column(
        DateTime(timezone = True),
        server_default = func.now()
    )
    user_id : Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id"),
        nullable = False,
        index = True
    )
    email : Mapped[str] = mapped_column(
        String(40),
        nullable = False,
        index = True
    )
    ip : Mapped[str] = mapped_column(
        String(40),
        nullable = False
    )
    browser : Mapped[str] = mapped_column(
        String(20),
        nullable = False
    )
    # Membuat relasi antara model LogActivity dan Users
    users = relationship("Users", back_populates = "log_activities")