import pytest
from app.providers.language.fast_detector import FastLanguageDetector


@pytest.mark.asyncio
async def test_english_language_detection():
    detector = FastLanguageDetector()
    res = await detector.detect("Yesterday I went to the market and bought some apples.")
    assert res.primary_language == "en"
    assert res.confidence >= 0.95
    assert not res.is_mixed
    assert "en" in res.detected_languages


@pytest.mark.asyncio
async def test_devanagari_hindi_detection():
    detector = FastLanguageDetector()
    res = await detector.detect("कल मैं बाज़ार गया और अपने दोस्त से मिला।")
    assert res.primary_language == "hi"
    assert "hi" in res.detected_languages


@pytest.mark.asyncio
async def test_hinglish_language_detection():
    detector = FastLanguageDetector()
    res = await detector.detect("Kal main market gaya tha aur bhai se mila.")
    assert res.primary_language == "hi"
    assert res.is_mixed is True
    assert "hi" in res.detected_languages
    assert "en" in res.detected_languages
