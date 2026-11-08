from pydantic import BaseModel
from datetime import datetime

from app.enums.product_enum import BrandEnum

class ProductVO(BaseModel):
    id: int
    product_name: str
    product_price: int
    product_stock: int
    product_brand: BrandEnum
    product_created_at: datetime | None = None

# DTO
class ProductCreateDTO(BaseModel):
    product_name: str
    product_price: int
    product_stock: int
    product_brand: BrandEnum
    product_created_at: datetime | None = None

    class Config:
        from_attributes = True

class ProductUpdateDTO(BaseModel):
    product_name: str | None = None
    product_price: int | None = None
    product_stock: int | None = None
    product_brand: BrandEnum | None = None
    product_created_at: datetime | None = None

    class Config:
        from_attributes = True

class ProductResponseDTO(BaseModel):
    id: int
    product_name: str
    product_price: int
    product_stock: int
    product_brand: BrandEnum
    product_created_at: datetime | None = None

    class Config:
        from_attributes = True