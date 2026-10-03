from app.core.config import settings
from app.providers.language.base import LanguageDetectionProvider
from app.providers.language.fast_detector import FastLanguageDetector


def get_language_detection_provider() -> LanguageDetectionProvider:
    provider_name = settings.LANGUAGE_DETECTION_PROVIDER.lower()
    if provider_name == "fast":
        return FastLanguageDetector()
    # Default fallback
    return FastLanguageDetector()
