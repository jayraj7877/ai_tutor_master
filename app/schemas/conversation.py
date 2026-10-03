from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from app.schemas.language import LanguageDetectionResult
from app.schemas.grammar import GrammarMistakeItem


class CreateConversationRequest(BaseModel):
    user_id: Optional[str] = Field(None, description="Optional user UUID")
    learning_language: str = Field(default="en", description="Target learning language")
    native_language: str = Field(default="hi", description="User's native language")
    difficulty: str = Field(default="intermediate", description="beginner, intermediate, advanced")
    voice_id: str = Field(default="female_01", description="Voice ID to use for TTS")
    speed: float = Field(default=0.95, ge=0.5, le=2.0, description="TTS speed multiplier")


class ConversationMessageRequest(BaseModel):
    conversation_id: str = Field(..., description="UUID of existing or new conversation session")
    message: str = Field(..., min_length=1, max_length=5000, description="User's input text")
    voice_id: str = Field(default="female_01", description="Voice ID for TTS audio")
    speed: float = Field(default=0.95, ge=0.5, le=2.0, description="TTS audio speed multiplier")
    user_id: Optional[str] = Field(None, description="Optional user ID for authorization/usage tracking")


class AudioChunkSchema(BaseModel):
    sequence: int = Field(..., description="1-indexed sequence number of audio chunk")
    format: str = Field(default="mp3", description="Audio encoding format e.g. mp3, wav")
    data: str = Field(..., description="Base64-encoded audio byte string")
    text: str = Field(..., description="Text segment corresponding to this audio chunk")


class ConversationMessageResponse(BaseModel):
    conversation_id: str
    user_message: str
    assistant_response: str
    language_info: LanguageDetectionResult
    grammar_analysis: List[GrammarMistakeItem]
    audio_chunks: List[AudioChunkSchema]
    metrics: Dict[str, float]


class MessageResponse(BaseModel):
    id: str
    conversation_id: str
    role: str
    text: str
    language: Optional[str]
    sequence_number: int
    created_at: datetime


class ConversationResponse(BaseModel):
    id: str
    user_id: Optional[str]
    learning_language: str
    native_language: Optional[str]
    difficulty: str
    voice_id: str
    speed: float
    title: Optional[str]
    created_at: datetime
    updated_at: datetime
    messages: Optional[List[MessageResponse]] = None
