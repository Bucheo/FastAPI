from fastapi import APIRouter, Depends, Query

from app.schemas.common_schema import ApiResponseDTO
from app.schemas.product_schema import ProductCreateDTO, ProductUpdateDTO
from app.services.product_service import ProductService, get_product_service


router = APIRouter()


# 상품 추가
@router.post(
    "",
    summary = "상품 등록",
    response_model = ApiResponseDTO
)
async def create_product(
    product: ProductCreateDTO,
    product_service: ProductService = Depends(get_product_service)
):
    new_product = await product_service.create_product(product)

    return ApiResponseDTO(
        success = True,
        message = "상품 등록 성공",
        data = {
            "newProductId": new_product
        }
    )

# 상품 전체 조회
@router.get(
    "",
    summary="상품 전체 조회",
    response_model=ApiResponseDTO
)
async def get_products(
    offset: int = Query(0, ge=0, description="시작 오프셋"),
    limit: int = Query(10, ge=1, le=100, description="가져올 갯수"),
    product_service: ProductService = Depends(get_product_service)
):
    found_products = await product_service.get_product_all(offset, limit)

    return ApiResponseDTO(
        success=True,
        message="전체 상품 조회 성공",
        data=found_products
    )

# 상품 전체 갯수 조회
@router.get(
    "/count",
    summary="상품 전체 갯수 조회",
    response_model=ApiResponseDTO
)
async def count_products(
    product_service: ProductService = Depends(get_product_service)
):
    total_count = await product_service.count_product()

    return ApiResponseDTO(
        success=True,
        message="상품 전체 갯수 조회 성공",
        data={
            "totalCount": total_count
        }
    )

# 상품 존재 여부 조회(id)
@router.get(
    "/exists/{id}",
    summary="상품 id로 상품 존재 여부 조회",
    response_model=ApiResponseDTO
)
async def exists_product_by_id(
    id: int,
    product_service: ProductService = Depends(get_product_service)
):
    exists_product = await product_service.exists_product_by_id(id)

    return ApiResponseDTO(
        success=True,
        message="상품 존재 여부 조회 성공",
        data={
            "exists": exists_product
        }
    )
    
# 상품 존재 여부 조회(name)
@router.get(
    "/exists",
    summary="상품명으로 상품 존재 여부 조회",
    response_model=ApiResponseDTO
)
async def exists_product_by_name(
    product_name: str = Query(..., min_length=1, max_length=20, description="조회할 상품명"),
    product_service: ProductService = Depends(get_product_service)
):
    exists_product = await product_service.exists_product_by_name(product_name)

    return ApiResponseDTO(
        success=True,
        message="상품 존재 여부 조회 성공",
        data={
            "exists": exists_product
        }
    )

# 상품 조회(id)
@router.get(
    "/{id}",
    summary="상품 조회(id)",
    response_model=ApiResponseDTO
)
async def find_product_by_id(
    id: int,
    product_service: ProductService = Depends(get_product_service)
):
    found_product = await product_service.get_product_by_id(id)

    return ApiResponseDTO(
        success=True,
        message="상품 조회 성공",
        data=found_product
    )

# 상품 수정
@router.put(
    "/{id}",
    summary="상품 수정",
    response_model=ApiResponseDTO
)
async def update_product(
    id: int,
    product: ProductUpdateDTO,
    product_service: ProductService = Depends(get_product_service)
):
    updated_product = await product_service.update_product(id, product)

    return ApiResponseDTO(
        success=True,
        message="상품 수정 성공",
        data=updated_product
    )

# 상품 삭제
@router.delete(
    "/{id}",
    summary="상품 삭제",
    response_model=ApiResponseDTO
)
async def delete_product(
    id: int,
    product_service: ProductService = Depends(get_product_service)
):
    await product_service.delete_product(id)

    return ApiResponseDTO(
        success=True,
        message="상품 삭제 성공",
        data=None
    )
























