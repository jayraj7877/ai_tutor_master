from abc import ABC, abstractmethod
from app.schemas.language import LanguageDetectionResult


class LanguageDetectionProvider(ABC):
    """Abstract Base Class for Language Detection Providers."""

    @abstractmethod
    async def detect(self, text: str) -> LanguageDetectionResult:
        """Detect primary and secondary languages in user text."""
        pass
