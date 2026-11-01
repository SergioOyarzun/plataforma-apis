from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class ProductoDB(Base):
    __tablename__ = "productos"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100), unique=True)
    precio: Mapped[int]
    stock: Mapped[int] = mapped_column(default=0)