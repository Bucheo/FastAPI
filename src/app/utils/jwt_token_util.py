import os
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError

from app.schemas.member_schema import MemberClaimDTO

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

# 에세스 토큰과 리프레쉬 토큰는 분리해서 구현하는 것이 좋다

# 1. access_token 생성하는 함수
def generate_access_token(member_claim: MemberClaimDTO) -> str:
    claims = member_claim.model_dump()
    
    # access_token: 1~5분
    expire = datetime.now(timezone.utc) + timedelta(days=1)
    access_token = jwt.encode(
        {
            **claims,
            "exp": expire
        },
        SECRET_KEY,
        algorithm=ALGORITHM
    )
    
    return access_token


# 2. refresh_token 생성하는 함수
def generate_refresh_token(member_claim: MemberClaimDTO) -> str:
    claims = member_claim.model_dump()
    
    # access_token: 1~5분
    expire = datetime.now(timezone.utc) + timedelta(days=30)
    refresh_token = jwt.encode(
        {
            **claims,
            "exp": expire
        },
        SECRET_KEY,
        algorithm=ALGORITHM
    )
    
    return refresh_token

# 3. token_parsing 함수 (token -> user_info)
def parse_token(token: str) -> MemberClaimDTO:
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    member_id = payload["id"]
    member_email = payload["member_email"]
    member_provider = payload["member_provider"]

    return MemberClaimDTO (
        id=member_id,
        member_email=member_email,
        member_provider=member_provider
    )

# 4. refresh_token을 이용해서 access_token 재발급
def reissue_access_token(refresh_token: str) -> str:
    claims = parse_token(refresh_token)
    new_access_token = generate_access_token(claims)
    return new_access_token
