# Mengimort pustaka yang diperlukan untuk model
from app.database.database import Base
from sqlalchemy import (
    BigInteger,
    String,
    Integer,
    Boolean,
    ForeignKey)
from sqlalchemy.orm import(
    Mapped,
    mapped_column,
    relationship)

# Membuat class Models untuk mendefinisikan model yang akan diimplementasikan ke sistem
class Models(Base):
    __tablename__ = "models"
    id: Mapped[int] = mapped_column(
        Integer, 
        primary_key = True,
        index = True,
        autoincrement = True)
    id_owner: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id"),
        nullable = False)
    models_name: Mapped[str] = mapped_column(
        String(50),
        nullable = False)
    model_type: Mapped[str] = mapped_column(
        String(10),
        nullable = False)
    url: Mapped[str] = mapped_column(
        String(255),
        nullable = False)
    is_active : Mapped[bool] = mapped_column(
        Boolean,
        default = True
    )

    # Membuat relasi antara model Models dan Users
    users = relationship("Users", back_populates = "models")

    # Membuat relasi antara model Models dan LeafCondition
    leaf_condition = relationship("LeafCondition", back_populates = "models")