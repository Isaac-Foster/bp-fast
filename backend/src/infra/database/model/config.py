from datetime import datetime

from sqlalchemy import (
    String,
    Integer,
    Boolean,
    DateTime,
)
from sqlalchemy.orm import Mapped, mapped_column


from src.infra.database.connect.sql import register


@register.mapped_as_dataclass
class ConfigModel:
    __tablename__ = 'config'

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, init=False
    )

    attempts: Mapped[int] = mapped_column(Integer, default=0, init=False)
    maintenance: Mapped[bool] = mapped_column(
        Boolean, default=False, init=False
    )
    maintenance_message: Mapped[str] = mapped_column(
        String(255), nullable=True, init=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, init=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, init=False
    )
