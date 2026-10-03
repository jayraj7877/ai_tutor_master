import re
import json
import httpx
from typing import List
from app.core.config import settings
from app.core.logging import logger
from app.providers.grammar.base import GrammarProvider
from app.schemas.grammar import GrammarAnalysisResult, GrammarMistakeItem


COMMON_GRAMMAR_RULES = [
    # Redundant / Conflicting Auxiliary Verbs (e.g., "What do are you?", "do is", "did went")
    (
        r'\bwhat\s+do\s+are\s+you\b',
        "do are", "are", "auxiliary_verb", "Do not combine 'do' and 'are'. Say 'What are you?' or 'What do you do?'."
    ),
    (
        r'\bdo\s+are\b',
        "do are", "are", "auxiliary_verb", "Redundant auxiliary verbs 'do' and 'are'. Use either 'do' or 'are'."
    ),
    (
        r'\bdo\s+is\b',
        "do is", "is", "auxiliary_verb", "Do not mix 'do' and 'is' together."
    ),
    (
        r'\bdid\s+(went|came|saw|bought|ate)\b',
        "did went", "did go", "double_past_tense", "When using 'did', use the base form of the verb (e.g., 'did go' instead of 'did went')."
    ),
    # Past tense with past time indicators (yesterday, last night, ago)
    (
        r'\b(yesterday|last\s+\w+|\d+\s+days?\s+ago)\s+.*?\b(I|you|he|she|they|we)\s+(go)\b',
        "I go", "I went", "verb_tense", "Use past tense 'went' when describing actions completed in the past."
    ),
    (
        r'\b(yesterday|last\s+\w+|\d+\s+days?\s+ago)\s+.*?\b(meet)\b',
        "meet", "met", "verb_tense", "Use the past tense 'met' because the event occurred in the past."
    ),
    (
        r'\b(I|you|we|they)\s+go\s+to\s+(market|office|school)\s+(yesterday|last\s+night)\b',
        "go", "went", "verb_tense", "Use past tense 'went' when referring to a past trip."
    ),
    (
        r'\bI\s+go\s+to\s+market\b',
        "I go", "I went", "verb_tense", "Use past tense 'went' for past actions or add an article like 'to the market'."
    ),
    (
        r'\bI\s+meet\s+my\s+friend\b',
        "I meet", "I met", "verb_tense", "Use past tense 'met' for past encounters."
    ),
    # Subject-verb agreement
    (
        r'\b(he|she|it)\s+(don\'t|dont)\b',
        "don't", "doesn't", "subject_verb_agreement", "Use 'doesn't' with third-person singular pronouns (he/she/it)."
    ),
    (
        r'\b(he|she|it)\s+have\b',
        "have", "has", "subject_verb_agreement", "Use 'has' with third-person singular pronouns."
    ),
    # Hinglish direct translation patterns
    (
        r'\bI\s+am\s+having\s+(\d+|two|three|a)\s+(brother|brothers|sister|sisters|car|cars)\b',
        "I am having", "I have", "phraseology", "Use 'I have' to express possession instead of 'I am having'."
    ),
    (
        r'\bwhat\s+is\s+your\s+good\s+name\b',
        "good name", "name", "phraseology", "Say 'May I know your name?' or 'What is your name?' in standard English."
    ),
]


class RuleAndLLMGrammarProvider(GrammarProvider):
    """Grammar engine combining high-speed pattern rules with LLM-based grammar checking."""

    async def analyze(self, text: str, language: str = "en") -> GrammarAnalysisResult:
        if not text or len(text.strip()) == 0:
            return GrammarAnalysisResult(mistakes=[])

        mistakes: List[GrammarMistakeItem] = []
        lower_text = text.lower()

        # Check verb tenses specifically for common patterns
        if "yesterday" in lower_text or "last" in lower_text:
            if re.search(r'\bi\s+go\b', text, re.IGNORECASE):
                mistakes.append(GrammarMistakeItem(
                    original="I go",
                    corrected="I went",
                    type="verb_tense",
                    explanation="Use the past tense 'went' because the action happened in the past."
                ))
            if re.search(r'\bi\s+meet\b', text, re.IGNORECASE):
                mistakes.append(GrammarMistakeItem(
                    original="I meet",
                    corrected="I met",
                    type="verb_tense",
                    explanation="Use the past tense 'met' for an event that happened in the past."
                ))

        # Run regex rules
        for pattern, orig, corr, m_type, expl in COMMON_GRAMMAR_RULES:
            if re.search(pattern, text, re.IGNORECASE):
                if not any(m.original.lower() == orig.lower() for m in mistakes):
                    mistakes.append(GrammarMistakeItem(
                        original=orig,
                        corrected=corr,
                        type=m_type,
                        explanation=expl
                    ))

        # Check general ungrammatical question structure if rules didn't catch anything
        if not mistakes and "do are" in lower_text:
            mistakes.append(GrammarMistakeItem(
                original="do are",
                corrected="are",
                type="auxiliary_verb",
                explanation="Do not mix auxiliary verbs 'do' and 'are' together."
            ))

        # Optional LLM fallback for non-rule-matched inputs if LLM_API_KEY is configured
        if not mistakes and settings.LLM_API_KEY and settings.LLM_PROVIDER in ["openai", "gemini"]:
            try:
                llm_mistakes = await self._analyze_with_llm(text, language)
                mistakes.extend(llm_mistakes)
            except Exception as e:
                logger.warning("LLM grammar analysis fallback failed", error=str(e))

        return GrammarAnalysisResult(mistakes=mistakes)

    async def _analyze_with_llm(self, text: str, language: str) -> List[GrammarMistakeItem]:
        prompt = (
            f"Analyze the following {language} sentence for grammatical errors: \"{text}\"\n"
            "Return JSON format:\n"
            "{\n"
            "  \"mistakes\": [\n"
            "    {\"original\": \"<incorrect phrase>\", \"corrected\": \"<corrected phrase>\", \"type\": \"<error type>\", \"explanation\": \"<short explanation>\"}\n"
            "  ]\n"
            "}"
        )

        headers = {"Authorization": f"Bearer {settings.LLM_API_KEY}", "Content-Type": "application/json"}
        payload = {
            "model": settings.LLM_MODEL or "gpt-4o-mini",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.0,
            "response_format": {"type": "json_object"}
        }

        base_url = settings.LLM_BASE_URL or "https://api.openai.com/v1"
        async with httpx.AsyncClient(timeout=5.0) as client:
            res = await client.post(f"{base_url}/chat/completions", headers=headers, json=payload)
            res.raise_for_status()
            data = res.json()
            raw_content = data["choices"][0]["message"]["content"]
            parsed = json.loads(raw_content)
            items = []
            for m in parsed.get("mistakes", []):
                items.append(GrammarMistakeItem(
                    original=m["original"],
                    corrected=m["corrected"],
                    type=m.get("type", "grammar"),
                    explanation=m.get("explanation", "Grammar correction.")
                ))
            return items
