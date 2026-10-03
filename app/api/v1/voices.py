from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.repositories.voice_repo import VoiceRepository
from app.schemas.voice import VoiceItem

router = APIRouter()


@router.get("/voices", response_model=List[VoiceItem])
async def list_voices(db: AsyncSession = Depends(get_db)):
    """List available voice options for TTS playback."""
    repo = VoiceRepository(db)
    voices = await repo.get_all_active()
    return [
        VoiceItem(
            voice_id=v.id,
            name=v.name,
            gender=v.gender,
            language=v.language,
            sample_url=v.sample_url,
            is_active=v.is_active,
        )
        for v in voices
    ]
