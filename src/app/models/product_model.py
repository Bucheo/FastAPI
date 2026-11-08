import enum
from datetime import date, datetime, timedelta, timezone

from sqlalchemy import BigInteger, Date, DateTime, Enum, Identity, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.enums.product_enum import BrandEnum
from app.infrastructure.postgresql import Base

KST = timezone(timedelta(hours=9)) # UTC+9

class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    product_name: Mapped[str] = mapped_column(String(100), nullable=False)
    product_price: Mapped[int] = mapped_column(Integer, nullable=False)
    product_stock: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    product_brand: Mapped[BrandEnum] = mapped_column(Enum(BrandEnum, native_enum=False), nullable=False)
    product_created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(KST)
    )