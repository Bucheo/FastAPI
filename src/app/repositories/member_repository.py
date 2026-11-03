from app.infrastructure.postgresql import get_postgresql_db
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

# 모델, ORM
from app.models.member_model import Member
from app.schemas.member_schema import (
    MemberCreateDTO
)
from sqlalchemy import insert, select, update, delete


# 이 클래스가 메모리에 할당 될 때 자동으로 DB에 주입되어야하기 떄문에 생성자를 만들어줘야 한다.
class MemberRepository:
    # 생성자 주입
    def __init__(self, db):
        self.db = db
    
    # 순수 함수
    # 1. 이메일 중복확인
    async def exists_member(self, member_email: str, member_provider: str) -> bool:
        query = select(Member).where(
            Member.member_email == member_email,
            Member.member_provider == member_provider
        )
        
        result = await self.db.execute(query)
        found_member = result.scalar_one_or_none()
        return found_member is not None
    
    # 2. 회원가입
    async def create_member(self, member: MemberCreateDTO):
        new_mbmer = {
            "member_email": member.member_email,
            "member_password": member.member_password,
            "member_name": member.member_name,
            "member_age": member.member_age,
            "member_profile": member.member_profile,
            "member_provider": member.member_provider
        }
    
    
    
    
    # 3. 소셜 회원가입
    # 4. 회원 정보 조회(id)
    # 5. 회원 정보 조회(email, provider)
    # 6. 회원 전체 정보 조회
    # 7. 회원 정보 수정
    # 8. 회원 삭제
        
# 주입 팩토리 메서드
def get_member_repository(db: AsyncSession = Depends(get_postgresql_db)):
    return MemberRepository(db)