# Mengimport pustaka yang dibutuhkan untuk model
from app.database.database import Base
from sqlalchemy import (
    Integer,
    String,
    Text,
    ForeignKey)
from sqlalchemy.orm import(
    Mapped,
    mapped_column,
    relationship)

# Membuat class LeafCondition untuk mendefinisikan kondisi daun
class LeafCondition(Base):
    __tablename__ = "leaf_condition"
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key = True,
        index = True,
        autoincrement = True)
    id_models: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("models.id"),
        index = True)
    condition: Mapped[str] = mapped_column(
        String(20),
        nullable = False)
    description: Mapped[str] = mapped_column(
        Text,
        nullable = False)
    treatment: Mapped[str] = mapped_column(
        Text, 
        nullable = False)
    image_reference: Mapped[str] = mapped_column(
        String(255),
        nullable = False)

    # Membuat relasi antara model LeafCondition dengan Predictions
    predictions = relationship("Predictions", back_populates = "leaf_condition")

    # Membuat relasi antara model LeafCondition dengan Models
    models = relationship("Models", back_populates = "leaf_condition")
    
    

