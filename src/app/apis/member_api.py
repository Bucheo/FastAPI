from fastapi import APIRouter, Query, Depends
from app.services.member_service import get_member_service, MemberService
from app.enums.member_enum import MemberProvider
from app.schemas.member_schema import MemberCreateDTO, MemberClaimDTO, MemberResponseDTO, MemberUpdateDTO
from app.schemas.common_schema import ApiResponseDTO

router = APIRouter()


@router.post(
    "/check-member", 
    response_model=ApiResponseDTO
)
async def check_member(
    member_email: str, 
    member_provider: str, 
    member_service = Depends(get_member_service)
):
    await member_service.check_duplicate_member(member_email, member_provider)
    return ApiResponseDTO(
        success=True,
        message="중복되지 않은 사용자",
    )


@router.post("/join",
    summary="회원 가입",
    response_model=ApiResponseDTO,
    responses={
        409: {
            "description": "중복된 이메일(또는 사용자 이름)으로 회원가입 시도",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "이미 존재하는 이메일입니다."
                    }
                }
            }
        }
}
)
async def join(
    member: MemberCreateDTO, 
    member_service: MemberService = Depends(get_member_service)
):
    if not member.member_provider:
        member.member_provider = MemberProvider.LOCAL.value
        
    # provider는 controller 담당
    member_claim: MemberClaimDTO = await member_service.join(member)

    return ApiResponseDTO(
        success=True,
        message="회원가입 성공",
        data=member_claim
    )

# 5. 회원 정보 조회(email, provider)
# 고정 경로(/search)는 /{id} 보다 위에 있어야 id로 해석되지 않는다.
@router.get(
    "/search",
    summary="이메일로 회원 조회",
    response_model=ApiResponseDTO,
)
# Query(...): 쿼리스트링으로 데이터를 받기 필수로 값을 받겠다는 뜻
async def get_member_by_email(
    email: str = Query(...),
    provider: MemberProvider = Query(...),
    member_service: MemberService = Depends(get_member_service)
):
    found_member = await member_service.find_member_by_email(email, provider)
    return ApiResponseDTO(
        success=True,
        message="회원 조회 성공",
        data=found_member
    )

# 6. 회원 전체 정보 조회
# @router.get(
#     "",
#     summary="회원 전체 조회",
#     response_model=ApiResponseDTO,
# )
# async def get_member_all(
#     member_service: MemberService = Depends(get_member_service)
# ):
#     return ApiResponseDTO(
#         success=True,
#         message="회원 전체 조회 성공",
#         data = await member_service.get_member_all()
#     )

# 실무 버전
@router.get(
    "",
    summary="회원 전체 조회",
    response_model=ApiResponseDTO,
)
async def get_member_all(
    offset: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    member_service: MemberService = Depends(get_member_service)
):
    page_result = await member_service.get_members_paging(offset, limit)
    
    return ApiResponseDTO(
        success=True,
        message="회원 전체 조회 성공",
        data = page_result
    )


@router.get(
    "/{id}",
    response_model=ApiResponseDTO,
)
async def get_member_by_id(
    id: int, 
    member_service: MemberService = Depends(get_member_service)
):
    found_member = await member_service.get_member_by_id(id)
    return ApiResponseDTO(
        success=True,
        message="회원 조회 성공",
        data=found_member
    )


@router.put(
    "/{id}",
    summary="회원 정보 수정",
    response_model=ApiResponseDTO
)
async def update_member(
    id: int,
    member: MemberUpdateDTO,
    member_service: MemberService = Depends(get_member_service)
):
    updated_member = await member_service.update_member(id, member)
    
    return ApiResponseDTO(
        success=True,
        message="회원 조회 성공",
        data=updated_member
    )

@router.delete(
    "/{id}",
    summary="회원 정보 삭제",
    response_model=ApiResponseDTO
)
async def withdraw(
    id: int,
    member_service: MemberService = Depends(get_member_service)
):
    await member_service.withdraw(id)
    
    return ApiResponseDTO(
        success=True,
        message="회원 삭제 성공"
    )