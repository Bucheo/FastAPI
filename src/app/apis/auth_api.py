import os
import secrets
from dotenv import load_dotenv
from fastapi import APIRouter, Query, Depends, Response, Request, HTTPException, status
from app.schemas.common_schema import ApiResponseDTO
from app.schemas.member_schema import MemberClaimDTO
from app.enums.member_enum import MemberProvider
from app.schemas.auth_schema import JwtTokenDTO, LoginRequestDTO, SocialLoginRequestDTO
from app.services.auth_service import AuthService, get_auth_service
from app.dependencies.auth_dependency import get_current_member, get_tokens

# 소셜 로그인용
import httpx # 추가 요청
from fastapi.responses import RedirectResponse # 페이지 전환
from urllib.parse import urlencode # 요청주소를 조합하기 위한 라이브러리


load_dotenv()
router = APIRouter()

@router.post(
    "/login",
    response_model=ApiResponseDTO,
    summary="로컬 로그인",
    responses={
        200: {
            "description": "로그인 성공"
        },
        400: {
            "description": "비밀번호 불일치 등 잘못된 요청",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "아이디 또는 비밀번호가 일치하지 않습니다."
                    }
                }
            }
        },
        404: {
            "description": "존재하지 않는 회원",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "회원이 존재하지 않습니다."
                    }
                }
            }
        }
    }
)
async def login(
    login_member: LoginRequestDTO,
    response: Response,
    auth_service: AuthService = Depends(get_auth_service)
):
    login_member.member_provider = MemberProvider.LOCAL.value
    tokens = await auth_service.login(login_member)

    access_token = tokens.access_token
    refresh_token = tokens.refresh_token

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=60 * 60 * 24 
    )

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=60 * 60 * 24 * 30
    )

    return ApiResponseDTO(
        success=True,
        message="로그인 성공"
    )


GOOGLE_AUTH_URL=os.getenv("GOOGLE_AUTH_URL")
GOOGLE_TOKEN_URL=os.getenv("GOOGLE_TOKEN_URL")
GOOGLE_USERINFO_URL=os.getenv("GOOGLE_USERINFO_URL")
GOOGLE_CLIENT_ID=os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET=os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI=os.getenv("GOOGLE_REDIRECT_URI")
FRONTEND_URL=os.getenv("FRONT_END_URL")  # .env 이름과 맞춰야 한다


# 구글 로그인
# /auth/google/
@router.get(
    "/google",
    summary="구글 로그인"
)
async def google_login():
    params = {
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "consent"
    }

    url = f"{GOOGLE_AUTH_URL}?{urlencode(params)}"
    return RedirectResponse(url)


# 구글 로그인 콜백
# /auth/google/callback
@router.get(
    "/google/callback",
    summary="구글 로그인 콜백"
)
async def google_login_callback(
    code: str,
    response: Response,
    auth_service: AuthService = Depends(get_auth_service)
):
    user = await _fetch_social_user(
        provider="구글",
        token_url=GOOGLE_TOKEN_URL,
        userinfo_url=GOOGLE_USERINFO_URL,
        token_data={
            "code": code,
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "redirect_uri": GOOGLE_REDIRECT_URI,
            "grant_type": "authorization_code"
        }
    )

    user_params = _make_user_params(
        provider=MemberProvider.GOOGLE,
        email=user.get("email"),
        provider_id=user.get("sub")
    )

    return await _handle_social_login(user_params, auth_service)



# 환경 변수로 들고오기
KAKAO_CLIENT_ID=os.getenv("KAKAO_CLIENT_ID")
KAKAO_CLIENT_SECRET=os.getenv("KAKAO_CLIENT_SECRET")
KAKAO_REDIRECT_URI=os.getenv("KAKAO_REDIRECT_URI")
KAKAO_AUTH_URL=os.getenv("KAKAO_AUTH_URL")
KAKAO_TOKEN_URL=os.getenv("KAKAO_TOKEN_URL")
KAKAO_USERINFO_URL=os.getenv("KAKAO_USERINFO_URL")

@router.get("/kakao", summary="카카오 로그인 리다이렉트")
async def kakao_login():
    params = {
        "client_id": KAKAO_CLIENT_ID,
        "redirect_uri": KAKAO_REDIRECT_URI,
        "response_type": "code",
        # "prompt": "login",  # 이미 카카오에 로그인돼 있어도 매번 로그인 화면을 띄운다
    }

    url = f"{KAKAO_AUTH_URL}?{urlencode(params)}"
    return RedirectResponse(url)

@router.get("/kakao/callback", summary="카카오 로그인 콜백")
async def kakao_login_callback(
    code: str,
    response: Response,
    auth_service: AuthService = Depends(get_auth_service)
):
    user = await _fetch_social_user(
        provider="카카오",
        token_url=KAKAO_TOKEN_URL,
        userinfo_url=KAKAO_USERINFO_URL,
        token_data={
            "code": code,
            "client_id": KAKAO_CLIENT_ID,
            "client_secret": KAKAO_CLIENT_SECRET,
            "redirect_uri": KAKAO_REDIRECT_URI,
            "grant_type": "authorization_code"
        }
    )

    # 카카오: 이메일은 kakao_account 안에, id는 최상위(숫자)
    user_params = _make_user_params(
        provider=MemberProvider.KAKAO,
        email=(user.get("kakao_account") or {}).get("email"),
        provider_id=user.get("id")
    )

    return await _handle_social_login(user_params, auth_service)


NAVER_CLIENT_ID=os.getenv("NAVER_CLIENT_ID")
NAVER_CLIENT_SECRET=os.getenv("NAVER_CLIENT_SECRET")
NAVER_REDIRECT_URI=os.getenv("NAVER_REDIRECT_URI")
NAVER_AUTH_URL=os.getenv("NAVER_AUTH_URL")
NAVER_TOKEN_URL=os.getenv("NAVER_TOKEN_URL")
NAVER_USERINFO_URL=os.getenv("NAVER_USERINFO_URL")


@router.get("/naver", summary="네이버 로그인 리다이렉트")
async def naver_login():
    # 네이버는 state가 필수 (CSRF 방지용 랜덤 값) -> 쿠키에 저장해 두고 콜백에서 비교
    state = secrets.token_urlsafe(16)
    params = {
        "client_id": NAVER_CLIENT_ID,
        "redirect_uri": NAVER_REDIRECT_URI,
        "response_type": "code",
        "state": state,
        # "auth_type": "reauthenticate",  # 이미 네이버에 로그인돼 있어도 매번 로그인 화면을 띄운다
    }

    url = f"{NAVER_AUTH_URL}?{urlencode(params)}"
    redirect_response = RedirectResponse(url)
    redirect_response.set_cookie(
        key="naver_state",
        value=state,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=60 * 5
    )
    return redirect_response


@router.get("/naver/callback", summary="네이버 로그인 콜백")
async def naver_login_callback(
    code: str,
    state: str,
    request: Request,
    auth_service: AuthService = Depends(get_auth_service)
):
    if state != request.cookies.get("naver_state"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="네이버 로그인 state 값이 일치하지 않습니다. 다시 로그인해주세요."
        )

    user = await _fetch_social_user(
        provider="네이버",
        token_url=NAVER_TOKEN_URL,
        userinfo_url=NAVER_USERINFO_URL,
        token_data={
            "code": code,
            "state": state,
            "client_id": NAVER_CLIENT_ID,
            "client_secret": NAVER_CLIENT_SECRET,
            "redirect_uri": NAVER_REDIRECT_URI,
            "grant_type": "authorization_code"
        }
    )

    # 네이버: 유저 정보가 response 안에 들어있다
    naver_user = user.get("response") or {}
    user_params = _make_user_params(
        provider=MemberProvider.NAVER,
        email=naver_user.get("email"),
        provider_id=naver_user.get("id")
    )

    redirect_response = await _handle_social_login(user_params, auth_service)
    redirect_response.delete_cookie("naver_state")
    return redirect_response



# 로그아웃
@router.post(
    "/logout",
    summary="로그아웃",
    response_model=ApiResponseDTO,
)
async def logout(
    response: Response,
    member_claims: MemberClaimDTO = Depends(get_current_member),
    tokens: JwtTokenDTO = Depends(get_tokens),
    auth_service: AuthService = Depends(get_auth_service)
):
    await auth_service.logout(member_claims.id, tokens)

    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")

    return ApiResponseDTO(
        success=True,
        message="로그아웃 성공"
    )

@router.get(
    "/refresh",
    response_model=ApiResponseDTO,
    summary="토큰 재발급"
)
async def refresh(
    response: Response,
    tokens: JwtTokenDTO = Depends(get_tokens),
    auth_service: AuthService = Depends(get_auth_service)
):
    refresh_token = tokens.refresh_token
    try:
        access_token = await auth_service.refresh(refresh_token)

        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=False,
            samesite="lax",
            max_age=60 * 60 * 24 
        )

        return ApiResponseDTO(
            success=True,
            message="Access Token 재발급 성공"
        )
    
    except Exception as e:
        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")

        return ApiResponseDTO(
            success=False,
            message="Refresh Token 만료"
        )



# ---------- 소셜 로그인 공통 함수 ----------

# code -> 소셜 access_token 발급 -> 유저 정보 조회
async def _fetch_social_user(provider: str, token_url: str, userinfo_url: str, token_data: dict) -> dict:
    async with httpx.AsyncClient() as client:
        token_res = await client.post(token_url, data=token_data)
        token_json = token_res.json()
        access_token = token_json.get("access_token")

        if not access_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"{provider} 토큰 발급 실패: {token_json}"
            )

        user_res = await client.get(
            userinfo_url,
            headers={"Authorization": f"Bearer {access_token}"}
        )
        return user_res.json()


# 소셜 유저 정보 -> join-additional 로 넘길 파라미터
def _make_user_params(provider: MemberProvider, email: str | None, provider_id) -> dict:
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{provider.value} 계정 이메일을 가져오지 못했습니다. 개발자 콘솔에서 이메일 제공 동의항목을 설정하세요."
        )

    return {
        "member_email": email,
        "member_provider": provider.value,
        "member_provider_id": str(provider_id)
    }


async def _handle_social_login(user_params: dict, auth_service: AuthService):
    social_member = SocialLoginRequestDTO.model_validate(user_params)
    tokens = await auth_service.social_login(social_member)

    # 비회원
    if not tokens:
        url = f"{FRONTEND_URL}/join-additional?{urlencode(user_params)}"
        return RedirectResponse(url)

    # 기존 회원 
    access_token = tokens.access_token
    refresh_token = tokens.refresh_token

    redirect_response = RedirectResponse(url=FRONTEND_URL)
    redirect_response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=60 * 60 * 24 
    )

    redirect_response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=60 * 60 * 24 * 30
    )

    return redirect_response


async def _handle_social_login_or_join(user_params: dict, auth_service: AuthService):
    social_member = SocialLoginRequestDTO.model_validate(user_params)
    tokens = await auth_service.social_login_or_join(social_member)

    access_token = tokens.access_token
    refresh_token = tokens.refresh_token

    redirect_response = RedirectResponse(url=FRONTEND_URL)
    redirect_response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=60 * 60 * 24 
    )

    redirect_response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=60 * 60 * 24 * 30
    )

    return redirect_response




