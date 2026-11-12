from fastapi import APIRouter, Form, Query, Depends, Response, UploadFile, File
from app.dependencies.auth_dependency import get_current_member
from app.schemas.s3_schema import ImageUploadResponseDTO
from app.services.member_service import get_member_service, MemberService
from app.services.auth_service import AuthService, get_auth_service
from app.enums.member_enum import MemberProvider
from app.enums.s3_enum import S3Folder
from app.services.s3_service import get_s3_service, S3Service
from app.schemas.auth_schema import SocialLoginRequestDTO
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
    response: Response,
    member_service: MemberService = Depends(get_member_service),
    auth_service: AuthService = Depends(get_auth_service)
):
    if not member.member_provider:
        member.member_provider = MemberProvider.LOCAL.value

    # provider는 controller 담당
    member_claim: MemberClaimDTO = await member_service.join(member)

    # 소셜(구글/카카오) 추가 가입이면 가입 직후 바로 로그인 처리 -> 토큰을 쿠키로 전달
    if member.member_provider != MemberProvider.LOCAL:
        tokens = await auth_service.social_login(
            SocialLoginRequestDTO(
                member_email=member.member_email,
                member_provider=member.member_provider,
                member_provider_id=member.member_provider_id
            )
        )

        response.set_cookie(
            key="access_token",
            value=tokens.access_token,
            httponly=True,
            secure=False,
            samesite="lax",
            max_age=60 * 60 * 24
        )
        response.set_cookie(
            key="refresh_token",
            value=tokens.refresh_token,
            httponly=True,
            secure=False,
            samesite="lax",
            max_age=60 * 60 * 24 * 30
        )

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
    "/{id}/profile",
    summary="회원 정보 수정",
    response_model=ApiResponseDTO
)
async def update_profile(
    id: int,
    file: UploadFile = File(...),
    folder: S3Folder = Form(...),
    s3_service: S3Service = Depends(get_s3_service),
    member_service: MemberService = Depends(get_member_service)
):
    result: ImageUploadResponseDTO = await s3_service.upload_image_with_thumbnail(
        file=file,
        folder=folder.value
    )
    
    original_url = result.original_url
    member_update_dto = MemberUpdateDTO(
        member_profile=original_url
    )

    updated_member = await member_service.update_member(id, member_update_dto)

    return ApiResponseDTO(
        success=True,
        message="프로필 수정 완료",
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
    
# access_token -> 사용자를 전달하는 서비스

@router.post(
    "/me",
    response_model=ApiResponseDTO,
    summary="Access Token으로 회원정보 조회"
)
async def me(
    current_member: MemberClaimDTO = Depends(get_current_member),
    member_service: MemberService = Depends(get_member_service)
):
    member_id = current_member.id
    found_member = await member_service.get_member_by_id(member_id)

    return ApiResponseDTO(
        success=True,
        message="회원 정보 조회 완료",
        data=found_member
    )