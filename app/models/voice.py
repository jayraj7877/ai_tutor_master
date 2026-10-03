from datetime import datetime, timezone
from sqlalchemy import String, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base


class Voice(Base):
    __tablename__ = "voices"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)  # e.g., "female_01"
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    gender: Mapped[str] = mapped_column(String(20), nullable=False)  # "female" or "male"
    language: Mapped[str] = mapped_column(String(10), default="en", nullable=False)
    provider_name: Mapped[str] = mapped_column(String(50), default="gtts", nullable=False)
    provider_voice_id: Mapped[str] = mapped_column(String(100), nullable=False)
    sample_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
