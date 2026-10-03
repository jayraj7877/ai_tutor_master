from typing import Optional
from pydantic import BaseModel, Field


class VoiceItem(BaseModel):
    voice_id: str = Field(..., description="Unique voice identifier, e.g., 'female_01'")
    name: str = Field(..., description="Display name for the voice")
    gender: str = Field(..., description="'female' or 'male'")
    language: str = Field(..., description="Language code e.g. 'en'")
    sample_url: Optional[str] = Field(None, description="URL for sample audio snippet")
    is_active: bool = Field(True, description="Whether voice is currently available")
