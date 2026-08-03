# Menginport pustaka yang dibutuhkan dalam model
from app.database.database import Base
from sqlalchemy import (
    BigInteger,
    String,
    DateTime,
    Boolean,
    Enum)
from sqlalchemy.orm import (
    relationship,
    Mapped,
    mapped_column)
from sqlalchemy.sql import func
from datetime import datetime
import enum
import uuid as uuid_lib

# Membuat class UserRole untuk mendefinisikan peran pengguna
class UserRole(str, enum.Enum):
    admin = "admin"
    petani = "petani"

# Membuat class Users untuk mendefinisikan model seluruh pengguna
class Users(Base):
    __tablename__ = "users" # Nama entitas tabel dalam basis data
    id : Mapped[int] = mapped_column(
        BigInteger, 
        primary_key = True, 
        index = True, 
        autoincrement = True)
    uuid : Mapped[str]= mapped_column(
        String(36),
        unique = True,
        default = lambda: str(uuid_lib.uuid4()),
        index = True)
    email : Mapped[str] = mapped_column(
        String(40),
        unique = True,
        index = True,
        nullable = False)
    role : Mapped[UserRole]= mapped_column(
        Enum(UserRole),
        nullable = False,
        default = UserRole.petani)
    is_active :Mapped[bool]= mapped_column(
        Boolean,
        default = True)
    created_at : Mapped[datetime] = mapped_column(
        DateTime(timezone = True),
        server_default = func.now())
    updated_at : Mapped[datetime] = mapped_column(
        DateTime(timezone = True),
        server_default = func.now(),
        onupdate = func.now())

    # Membuat relasi antara model Users dan Profiles
    profiles = relationship("Profiles", back_populates = "users")

    # Membuat relasi antara model Users dan LogActivity
    log_activities = relationship("LogActivity", back_populates = "users")

    # Membuat relasi antara model Users dan Predictions
    predictions = relationship("Predictions", back_populates = "users")

    # Membuat relasi antara model Users dan Models
    models = relationship("Models", back_populates = "users")
