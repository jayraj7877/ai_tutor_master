import re
from app.providers.language.base import LanguageDetectionProvider
from app.schemas.language import LanguageDetectionResult


HINGLISH_KEYWORDS = {
    "kal", "hai", "kaise", "bhai", "main", "hu", "hoon", "kya", "toh", "aaj",
    "jaise", "par", "raha", "rahi", "huan", "gaya", "gayi", "karna", "sekho",
    "kahan", "kaun", "kaisa", "achha", "bahut", "yaar", "namaste", "shukriya"
}

DEVANAGARI_REGEX = re.compile(r'[\u0900-\u097F]')


class FastLanguageDetector(LanguageDetectionProvider):
    """Rule-based and heuristic language detector supporting English, Hindi, and Hinglish."""

    async def detect(self, text: str) -> LanguageDetectionResult:
        clean_text = text.strip()
        if not clean_text:
            return LanguageDetectionResult(
                primary_language="en",
                confidence=1.0,
                detected_languages=["en"],
                is_mixed=False
            )

        # Check for Hindi Devanagari script
        devanagari_chars = len(DEVANAGARI_REGEX.findall(clean_text))
        total_chars = len(clean_text)

        if devanagari_chars / max(total_chars, 1) > 0.3:
            # Check if there are also English words
            has_english_words = bool(re.search(r'[a-zA-Z]{2,}', clean_text))
            if has_english_words:
                return LanguageDetectionResult(
                    primary_language="hi",
                    confidence=0.92,
                    detected_languages=["hi", "en"],
                    is_mixed=True
                )
            return LanguageDetectionResult(
                primary_language="hi",
                confidence=0.98,
                detected_languages=["hi"],
                is_mixed=False
            )

        # Check for Romanized Hindi / Hinglish
        words = [w.lower().strip(".,!?") for w in clean_text.split()]
        hinglish_count = sum(1 for w in words if w in HINGLISH_KEYWORDS)

        if hinglish_count > 0:
            return LanguageDetectionResult(
                primary_language="hi",
                confidence=min(0.85 + (hinglish_count * 0.05), 0.98),
                detected_languages=["hi", "en"],
                is_mixed=True
            )

        # Default to English
        return LanguageDetectionResult(
            primary_language="en",
            confidence=0.98,
            detected_languages=["en"],
            is_mixed=False
        )
