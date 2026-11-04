from sqlalchemy import BigInteger, Enum, ForeignKey, UniqueConstraint, DateTime, Identity, Text, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, timedelta, timezone

# PostgreSQL의 Base를 상속받아서 서버가 켜질 때 동기화시킨다.
from app.infrastructure.postgresql import Base
from typing import TYPE_CHECKING

# ※ 순환 참조
if TYPE_CHECKING:
    from app.models.member_model import Member

KST = timezone(timedelta(hours=9)) # UTC+9

class Post(Base):
    __tablename__ = "posts"
    
    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    post_title: Mapped[str] = mapped_column(Text, nullable=False)
    post_content: Mapped[str] = mapped_column(Text, nullable=False)
    post_read_count: Mapped[int] = mapped_column(BigInteger)
    # post_like: 외부 테이블을 관계로 맺고 테이블의 길이를 세는 것
    
    post_updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(KST)
    )
    
    post_created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(KST)
    )
    
    # 관계
    member_id: Mapped[int] = mapped_column(ForeignKey("members.id"), nullable=False)
    member: Mapped["Member"] = relationship("Member", back_populates="posts")
    
    
    
    
    