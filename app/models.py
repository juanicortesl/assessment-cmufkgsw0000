from datetime import datetime
from sqlalchemy import Boolean, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class Item(Base):
    __tablename__ = "items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)


class Client(Base):
    __tablename__ = "clients"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    rut: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=True)
    phone: Mapped[str] = mapped_column(String(50), nullable=True)
    address: Mapped[str] = mapped_column(String(255), nullable=True)
    commune: Mapped[str] = mapped_column(String(100), nullable=True)
    region: Mapped[str] = mapped_column(String(100), nullable=True)
    estado_civil: Mapped[str] = mapped_column(String(100), nullable=True)
    profesion_oficio: Mapped[str] = mapped_column(String(150), nullable=True)
    is_migrated: Mapped[bool] = mapped_column(Boolean, default=False)


class NotarialDeed(Base):
    __tablename__ = "notarial_deeds"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    document_code: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    deed_type: Mapped[str] = mapped_column(String(100), nullable=False, default="PODER_ESPECIAL")
    customer_rut: Mapped[str] = mapped_column(String(50), nullable=False)
    payment_id: Mapped[str] = mapped_column(String(100), nullable=False)
    payment_status: Mapped[str] = mapped_column(String(50), nullable=False, default="COMPLETED")
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="PENDING")
    rendered_content: Mapped[str] = mapped_column(Text, nullable=True)
    error_log: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
