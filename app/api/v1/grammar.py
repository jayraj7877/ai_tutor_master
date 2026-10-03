from fastapi import APIRouter
from app.schemas.grammar import GrammarCheckRequest, GrammarAnalysisResult
from app.providers.grammar.factory import get_grammar_provider

router = APIRouter()


@router.post("/grammar/check", response_model=GrammarAnalysisResult)
async def check_grammar(request: GrammarCheckRequest):
    """Standalone grammar analysis endpoint."""
    provider = get_grammar_provider()
    return await provider.analyze(request.text, language=request.language)
