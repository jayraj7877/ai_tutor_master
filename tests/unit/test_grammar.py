import pytest
from app.providers.grammar.rule_llm_grammar import RuleAndLLMGrammarProvider


@pytest.mark.asyncio
async def test_grammar_correct_sentence():
    provider = RuleAndLLMGrammarProvider()
    res = await provider.analyze("Yesterday I went to the market and met my friend.", language="en")
    assert len(res.mistakes) == 0


@pytest.mark.asyncio
async def test_grammar_incorrect_tense():
    provider = RuleAndLLMGrammarProvider()
    res = await provider.analyze("Yesterday I go to market and I meet my friend.", language="en")
    assert len(res.mistakes) >= 2
    originals = [m.original for m in res.mistakes]
    assert "I go" in originals
    assert "I meet" in originals
    types = [m.type for m in res.mistakes]
    assert "verb_tense" in types


@pytest.mark.asyncio
async def test_grammar_hinglish_phraseology():
    provider = RuleAndLLMGrammarProvider()
    res = await provider.analyze("I am having two brothers.", language="en")
    assert len(res.mistakes) >= 1
    assert res.mistakes[0].corrected == "I have"


@pytest.mark.asyncio
async def test_grammar_auxiliary_verb_conflict():
    provider = RuleAndLLMGrammarProvider()
    res = await provider.analyze("What do are you ?", language="en")
    assert len(res.mistakes) >= 1
    assert res.mistakes[0].original == "do are"
    assert res.mistakes[0].type == "auxiliary_verb"
