from app.core.config import settings
from app.providers.grammar.base import GrammarProvider
from app.providers.grammar.rule_llm_grammar import RuleAndLLMGrammarProvider


def get_grammar_provider() -> GrammarProvider:
    provider_name = settings.GRAMMAR_PROVIDER.lower()
    if provider_name == "rule_llm":
        return RuleAndLLMGrammarProvider()
    return RuleAndLLMGrammarProvider()
