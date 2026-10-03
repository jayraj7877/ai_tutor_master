import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Text, DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


def generate_uuid() -> str:
    return str(uuid.uuid4())


class GrammarMistake(Base):
    __tablename__ = "grammar_mistakes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    message_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("messages.id", ondelete="CASCADE"), nullable=True, index=True)
    conversation_id: Mapped[str] = mapped_column(String(36), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True)
    original_text: Mapped[str] = mapped_column(String(255), nullable=False)
    corrected_text: Mapped[str] = mapped_column(String(255), nullable=False)
    mistake_type: Mapped[str] = mapped_column(String(50), default="grammar", nullable=False)
    explanation: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    message = relationship("Message", back_populates="grammar_mistakes")
    conversation = relationship("Conversation", back_populates="grammar_mistakes")

    __table_args__ = (
        Index("idx_grammar_mistakes_conversation_id", "conversation_id"),
        Index("idx_grammar_mistakes_message_id", "message_id"),
    )
