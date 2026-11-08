from fastapi import Depends, HTTPException

from app.repositories.product_repository import ProductRepository, get_product_repository
from app.schemas.common_schema import PageResponseDTO
from app.schemas.product_schema import ProductCreateDTO, ProductResponseDTO, ProductUpdateDTO


class ProductService:
    def __init__(self, repo: ProductRepository):
        self.repo = repo

    # 상품 추가
    async def create_product(self, product: ProductCreateDTO) -> int:
        exists_product = await self.exists_product_by_name(product.product_name)
        if exists_product:
            raise HTTPException(
                status_code = 409,
                detail = "이미 존재하는 상품명입니다."
            )

        new_product_id = await self.repo.create_product(product)
        return new_product_id

    # 상품 조회(id)
    async def get_product_by_id(self, id: int) -> ProductResponseDTO:
        found_product = await self.repo.find_product_by_id(id)
        if not found_product:
            raise HTTPException(
                status_code = 404,
                detail = "상품이 존재하지 않습니다."
            )

        return ProductResponseDTO.model_validate(found_product)

    # 상품 전체 조회
    async def get_product_all(self, offset: int = 0, limit: int = 10) -> PageResponseDTO:
        products = await self.repo.find_product_all(offset, limit)
        total_count = await self.repo.count_product()
        total_pages = (total_count + limit - 1) // limit if limit > 0 else 1
        items_dto = [ProductResponseDTO.model_validate(product) for product in products]

        return PageResponseDTO[ProductResponseDTO] (
            total_count = total_count,
            total_pages = total_pages,
            offset = offset,
            limit = limit,
            items = items_dto
        )

    # 상품 전체 갯수 조회
    async def count_product(self) -> int:
        return await self.repo.count_product()


    # 상품 존재 여부 조회(id)
    async def exists_product_by_id(self, id: int) -> bool:
        return await self.repo.exists_product_by_id(id)

    # 상품 존재 여부 조회(name)
    async def exists_product_by_name(self, product_name: str) -> bool:
        return await self.repo.exists_product_by_name(product_name)

    # 상품 수정
    async def update_product(self, id: int, product: ProductUpdateDTO):
        exists_product = await self.exists_product_by_id(id)
        if not exists_product:
            raise HTTPException(
                status_code=404,
                detail="상품이 존재하지 않습니다."
            )

        updated_product = await self.repo.update_product(id, product)

        return ProductResponseDTO.model_validate(updated_product)

    # 상품 삭제
    async def delete_product(self, id: int):
        is_deleted = await self.repo.exists_product_by_id(id)
        if not is_deleted:
            raise HTTPException(
                status_code=404,
                detail="상품이 존재하지 않습니다."
            ) 

        await self.repo.delete_product(id)

def get_product_service(repo: ProductRepository = Depends(get_product_repository)):
    return ProductService(repo)