from typing import List
from pydantic import BaseModel, Field


class LanguageDetectRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=5000, description="Text to analyze")


class LanguageDetectionResult(BaseModel):
    primary_language: str = Field(..., description="ISO language code, e.g., 'en', 'hi'")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score between 0.0 and 1.0")
    detected_languages: List[str] = Field(default_factory=list, description="List of detected ISO language codes")
    is_mixed: bool = Field(default=False, description="True if text contains multiple languages e.g., Hinglish")
