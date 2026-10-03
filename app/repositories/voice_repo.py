from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.voice import Voice

DEFAULT_VOICES = [
    Voice(
        id="female_01",
        name="Emma (Female - US)",
        gender="female",
        language="en",
        provider_name="gtts",
        provider_voice_id="en-US-Neural",
        sample_url="http://localhost:8000/samples/female_01_sample.mp3",
        is_active=True,
    ),
    Voice(
        id="male_01",
        name="James (Male - UK/US)",
        gender="male",
        language="en",
        provider_name="gtts",
        provider_voice_id="en-GB-Male",
        sample_url="http://localhost:8000/samples/male_01_sample.mp3",
        is_active=True,
    ),
    Voice(
        id="female_02",
        name="Priya (Female - Indian/Hinglish)",
        gender="female",
        language="hi",
        provider_name="gtts",
        provider_voice_id="hi-IN-Female",
        sample_url="http://localhost:8000/samples/female_02_sample.mp3",
        is_active=True,
    ),
    Voice(
        id="male_02",
        name="Rohan (Male - Indian/Hinglish)",
        gender="male",
        language="hi",
        provider_name="gtts",
        provider_voice_id="hi-IN-Male",
        sample_url="http://localhost:8000/samples/male_02_sample.mp3",
        is_active=True,
    ),
]


class VoiceRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all_active(self) -> List[Voice]:
        stmt = select(Voice).where(Voice.is_active == True)
        res = await self.db.execute(stmt)
        voices = list(res.scalars().all())
        if not voices:
            for v in DEFAULT_VOICES:
                self.db.add(v)
            await self.db.commit()
            return DEFAULT_VOICES
        return voices
