from fastapi import APIRouter
from app.schemas.language import LanguageDetectRequest, LanguageDetectionResult
from app.providers.language.factory import get_language_detection_provider

router = APIRouter()


@router.post("/language/detect", response_model=LanguageDetectionResult)
async def detect_language(request: LanguageDetectRequest):
    """Detect primary language and evaluate mixed-language/Hinglish text."""
    provider = get_language_detection_provider()
    return await provider.detect(request.text)
