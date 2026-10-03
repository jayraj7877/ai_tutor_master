from abc import ABC, abstractmethod
from app.schemas.grammar import GrammarAnalysisResult


class GrammarProvider(ABC):
    """Abstract Base Class for Grammar Analysis Providers."""

    @abstractmethod
    async def analyze(self, text: str, language: str = "en") -> GrammarAnalysisResult:
        """Analyze user text for grammatical mistakes in the target learning language."""
        pass
