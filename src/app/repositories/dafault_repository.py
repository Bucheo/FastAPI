from app.infrastructure.postgresql import get_postgresql_db
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

# 이 클래스가 메모리에 할당 될 때 자동으로 DB에 주입되어야하기 떄문에 생성자를 만들어줘야 한다.
class DefaultRepository:
    # 생성자 주입
    def __init__(self, db):
        self.db = db
    
    # 순수 함수
        
# 주입 팩토리 메서드
def get_default_repository(db: AsyncSession = Depends(get_postgresql_db)):
    return DefaultRepository(db)