from fastapi import Depends
from sqlalchemy import delete, exists, func, insert, select, update

from app.infrastructure.postgresql import get_postgresql_db
from app.models.product_model import Product
from app.schemas.product_schema import ProductCreateDTO, ProductUpdateDTO
from sqlalchemy.ext.asyncio import AsyncSession

class ProductRepository:
    def __init__(self, db):
        self.db = db

    # 상품 추가
    async def create_product(self, product: ProductCreateDTO):
        new_product = product.model_dump(exclude_none=True)
        query = (
            insert(Product)
            .values(**new_product)
            .returning(Product.id)
        )
        result = await self.db.execute(query)
        await self.db.commit()
        new_product = result.scalar_one()
        return new_product

    # 상품 조회(id)
    async def find_product_by_id(self, id: int):
        query = select(Product).where(Product.id == id)
        result = await self.db.execute(query)
        found_product = result.scalar_one_or_none()
        return found_product

    # 상품 전체 조회
    async def find_product_all(self, offset: int, limit: int) -> list[Product]:
        query = (
            select(Product)
            .offset(offset)
            .limit(limit)
        )
        result = await self.db.execute(query)
        found_product = result.scalars().all()
        return found_product

    # 상품 전체 갯수 조회
    async def count_product(self) -> int:
        query = select(func.count()).select_from(Product)
        result = await self.db.execute(query)
        count_stock = result.scalar_one()
        return count_stock

    # 상품 존재 여부 조회(id)
    async def exists_product_by_id(self, id: int) -> bool:
        query = select(exists().where(Product.id == id))

        result = await self.db.execute(query)
        exists_product = result.scalar_one()
        return exists_product

    # 상품 존재 여부 조회(name)
    async def exists_product_by_name(self, product_name: str) -> bool:
        query = select(exists().where(Product.product_name == product_name))
        result = await self.db.execute(query)
        exists_product = result.scalar_one()
        return exists_product

    # 상품 수정
    async def update_product(self, id: int, product: ProductUpdateDTO):
        data = product.model_dump(exclude_unset=True)

        if not data:
            return await self.find_product_by_id(id)

        query = (
            update(Product)
            .where(Product.id == id)
            .values(**data)
            .returning(Product)
        )
        result = await self.db.execute(query)
        await self.db.commit()
        updated_product = result.scalar_one_or_none()
        return updated_product


    # 상품 삭제
    async def delete_product(self, id: int):
        query = delete(Product).where(Product.id == id)
        result = await self.db.execute(query)
        await self.db.commit()
        return result.rowcount > 0

# 주입 팩토리 메서드
def get_product_repository(db: AsyncSession = Depends(get_postgresql_db)):
    return ProductRepository(db)