# Mengimort pustaka yang diperlukan untuk model
from app.database.database import Base
from sqlalchemy import (
    BigInteger,
    Integer,
    String,
    Float,
    DateTime,
    ForeignKey)
from sqlalchemy.orm import(
    Mapped,
    mapped_column,
    relationship)
from sqlalchemy.sql import func
from datetime import datetime
import uuid as uuid_lib

# Membuat class Predictions untuk mendefinisikan model seluruh prediksi pengguna
class Predictions(Base):
    __tablename__ = "predictions" # Nama entitas tabel dalam basis data
    id : Mapped[int] = mapped_column(
        BigInteger,
        primary_key = True,
        index = True,
        autoincrement = True)
    uuid : Mapped[str] = mapped_column(
        String(36),
        unique = True,
        default = lambda: str(uuid_lib.uuid4()))
    image_path : Mapped[str] = mapped_column(
        String(255),
        nullable = False)
    confidence : Mapped[float] = mapped_column(
        Float,
        nullable = False)
    created_at : Mapped[datetime] = mapped_column(
        DateTime(timezone = True),
        server_default = func.now())
    owner_id : Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id"),
        nullable = False,
        index = True)
    leaf_condidition_id : Mapped[int] = mapped_column(
        Integer,
        ForeignKey("leaf_condition.id"),
        nullable = False,
        index = True)

    # Membuat relasi antara model Predictions dan Users
    users = relationship("Users", back_populates = "predictions")

    # Membuat relasi antatara model Predictions dan LeafCondition
    leaf_condition = relationship("LeafCondition", back_populates = "predictions")
    