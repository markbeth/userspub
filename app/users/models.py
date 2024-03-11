from app.database import Base

from datetime import datetime, UTC, date
from sqlalchemy.orm import Mapped, mapped_column


class User(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str]
    password_hashed: Mapped[bytes]
    verification_code: Mapped[str]
    is_verified: Mapped[bool] = mapped_column(default=False) 
    portfolio_id: Mapped[int | None]
    is_sub: Mapped[bool] = mapped_column(default=False) 
    is_admin: Mapped[bool] = mapped_column(default=False) 
    is_moder: Mapped[bool] = mapped_column(default=False)
    created: Mapped[date] = mapped_column(default=datetime.now(UTC).date())
