from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.models.conversation import Conversation


class ConversationRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, conversation_id: str, include_messages: bool = False) -> Optional[Conversation]:
        query = select(Conversation).where(Conversation.id == conversation_id)
        if include_messages:
            query = query.options(selectinload(Conversation.messages))
        result = await self.db.execute(query)
        return result.scalars().first()

    async def create(
        self,
        conversation_id: Optional[str] = None,
        user_id: Optional[str] = None,
        learning_language: str = "en",
        native_language: str = "hi",
        difficulty: str = "intermediate",
        voice_id: str = "female_01",
        speed: float = 0.95,
        title: Optional[str] = None,
    ) -> Conversation:
        kwargs = {
            "user_id": user_id,
            "learning_language": learning_language,
            "native_language": native_language,
            "difficulty": difficulty,
            "voice_id": voice_id,
            "speed": speed,
            "title": title or "English Conversation",
        }
        if conversation_id:
            kwargs["id"] = conversation_id

        conv = Conversation(**kwargs)
        self.db.add(conv)
        await self.db.commit()
        await self.db.refresh(conv)
        return conv

    async def get_or_create(
        self,
        conversation_id: str,
        user_id: Optional[str] = None,
        voice_id: str = "female_01",
        speed: float = 0.95,
    ) -> Conversation:
        existing = await self.get_by_id(conversation_id)
        if existing:
            return existing
        return await self.create(
            conversation_id=conversation_id,
            user_id=user_id,
            voice_id=voice_id,
            speed=speed,
        )
