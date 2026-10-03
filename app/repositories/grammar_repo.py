from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.grammar_mistake import GrammarMistake
from app.schemas.grammar import GrammarMistakeItem


class GrammarRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def save_mistakes(
        self,
        conversation_id: str,
        message_id: Optional[str],
        mistakes: List[GrammarMistakeItem],
    ) -> List[GrammarMistake]:
        records = []
        for m in mistakes:
            rec = GrammarMistake(
                conversation_id=conversation_id,
                message_id=message_id,
                original_text=m.original,
                corrected_text=m.corrected,
                mistake_type=m.type,
                explanation=m.explanation,
            )
            self.db.add(rec)
            records.append(rec)

        if records:
            await self.db.commit()
            for r in records:
                await self.db.refresh(r)
        return records

    async def get_by_conversation(self, conversation_id: str) -> List[GrammarMistake]:
        stmt = select(GrammarMistake).where(GrammarMistake.conversation_id == conversation_id)
        res = await self.db.execute(stmt)
        return list(res.scalars().all())
