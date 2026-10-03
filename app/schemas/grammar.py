from typing import List, Optional
from pydantic import BaseModel, Field


class GrammarCheckRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=5000, description="Text to check for grammar")
    language: str = Field(default="en", description="Target learning language to analyze")


class GrammarMistakeItem(BaseModel):
    original: str = Field(..., description="Original incorrect text snippet")
    corrected: str = Field(..., description="Suggested correction")
    type: str = Field(..., description="Type of error, e.g., verb_tense, article, preposition, vocabulary")
    explanation: str = Field(..., description="Explanation of why the correction is needed")


class GrammarAnalysisResult(BaseModel):
    mistakes: List[GrammarMistakeItem] = Field(default_factory=list, description="List of detected mistakes")
