# 설정의 책임 분리 (Separation of Concerns)
from app.infrastructure.redis import get_redis_db
from fastapi import Depends
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert, select, update, delete, func, exists

# 이 클래스가 메모리에 할당 될 때 자동으로 DB에 주입되어야하기 떄문에 생성자를 만들어줘야 한다.
class RedisRepository:
    # 생성자 주입
    def __init__(self, redis_client: Redis):
        self.redis_client = redis_client
    
    # 순수 함수
    async def set(self, key: str, value: str, ex: int = 3600) -> None:
        await self.redis_client.set(key, value, ex=ex)

    async def get(self, key: str) -> str | None:
        return await self.redis_client.get(key)
    
    async def exists(self, key: str) -> bool:
        result = await self.redis_client.exists(key)
        return result > 0
    
    async def delete(self, key: str) -> None:
        await self.redis_client.delete(key)
        
# 주입 팩토리 메서드
def get_redis_repository(redis_client: AsyncSession = Depends(get_redis_db)):
    return RedisRepository(redis_client)