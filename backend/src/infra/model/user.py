from datetime import datetime

from sqlalchemy import (
    String,
    Integer,
    Boolean,
    DateTime,
)
from sqlalchemy.orm import Mapped, mapped_column


from src.infra.connect.sql import register


@register.mapped_as_dataclass
class UserModel:
    __tablename__ = 'users'

    id: int = mapped_column(
        Integer, primary_key=True, autoincrement=True, init=False
    )
    username: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    password: Mapped[str] = mapped_column(String(128))

    logged_in: Mapped[bool] = mapped_column(Boolean, default=False, init=False)

    secret_otp: Mapped[str] = mapped_column(String(128), nullable=True)
    otp: Mapped[bool] = mapped_column(Boolean, default=False, nullable=True)
    allowed: Mapped[bool] = mapped_column(Boolean, default=True, init=False)

    attempts: Mapped[int] = mapped_column(Integer, default=0, init=False)
    blocked: Mapped[bool] = mapped_column(Boolean, default=False, init=False)

    last_login: Mapped[datetime] = mapped_column(default=None, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, init=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, init=False
    )
