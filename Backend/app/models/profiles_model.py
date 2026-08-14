# Mengimport pustaka yang dibutuhkan dalam model
from app.database.database import Base
from sqlalchemy import(
    BigInteger,
    String,
    DateTime,
    ForeignKey)
from sqlalchemy.sql import func
from sqlalchemy.orm import(
    relationship,
    Mapped,
    mapped_column)
from datetime import datetime

# Membuat class Profiles untuk mendefinisikan model seluruh profil pengguna
class Profiles(Base):
    __tablename__ = "profiles" # Nama entitas tabel dalam basis data
    id : Mapped[int] = mapped_column(
        BigInteger,
        primary_key = True,
        index = True,
        autoincrement = True)
    full_name : Mapped[str] = mapped_column(
        String(50),
        nullable = True,
        index = True)
    address : Mapped[str] = mapped_column(
        String(50),
        nullable = True,
        index = True)
    phone_number : Mapped[str] = mapped_column(
        String(20),
        nullable = True,
        index = True)
    created_at : Mapped[datetime]= mapped_column(
        DateTime(timezone = True),
         server_default = func.now())
    updated_at : Mapped[datetime] = mapped_column(
        DateTime(timezone = True),
        server_default = func.now(),
        onupdate = func.now())
    avatar : Mapped[str] = mapped_column(
        String(255),
        nullable = True,
        default = "app/static/profile_images/avatar/avatar_img.jpg"
    )
    user_id : Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id"),
        nullable = False,
        index = True
    )
    # Membuat relasi antara model Profiles dan Users
    users = relationship("Users", back_populates = "profiles")