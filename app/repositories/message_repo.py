from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.message import Message


class MessageRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def add_message(
        self,
        conversation_id: str,
        role: str,
        text: str,
        language: Optional[str] = "en",
    ) -> Message:
        # Get next sequence number
        stmt = select(func.coalesce(func.max(Message.sequence_number), 0)).where(
            Message.conversation_id == conversation_id
        )
        res = await self.db.execute(stmt)
        max_seq = res.scalar_one()

        msg = Message(
            conversation_id=conversation_id,
            role=role,
            text=text,
            language=language,
            sequence_number=max_seq + 1,
        )
        self.db.add(msg)
        await self.db.commit()
        await self.db.refresh(msg)
        return msg

    async def get_conversation_history(self, conversation_id: str, limit: int = 20) -> List[Message]:
        stmt = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.sequence_number.asc())
            .limit(limit)
        )
        res = await self.db.execute(stmt)
        return list(res.scalars().all())
