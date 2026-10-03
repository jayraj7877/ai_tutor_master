from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.orchestrator.conversation_orchestrator import ConversationOrchestrator
from app.repositories.conversation_repo import ConversationRepository
from app.repositories.message_repo import MessageRepository
from app.schemas.conversation import (
    CreateConversationRequest,
    ConversationMessageRequest,
    ConversationMessageResponse,
    ConversationResponse,
    MessageResponse,
)

router = APIRouter()


@router.post("/conversation", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
async def create_conversation(request: CreateConversationRequest, db: AsyncSession = Depends(get_db)):
    """Creates a new conversation session."""
    repo = ConversationRepository(db)
    conv = await repo.create(
        user_id=request.user_id,
        learning_language=request.learning_language,
        native_language=request.native_language,
        difficulty=request.difficulty,
        voice_id=request.voice_id,
        speed=request.speed,
    )
    return ConversationResponse(
        id=conv.id,
        user_id=conv.user_id,
        learning_language=conv.learning_language,
        native_language=conv.native_language,
        difficulty=conv.difficulty,
        voice_id=conv.voice_id,
        speed=conv.speed,
        title=conv.title,
        created_at=conv.created_at,
        updated_at=conv.updated_at,
    )


@router.post("/conversation/message", response_model=ConversationMessageResponse)
async def send_message(request: ConversationMessageRequest, db: AsyncSession = Depends(get_db)):
    """Primary Android endpoint: Sends user text, triggers pipeline, returns response & audio chunks."""
    orchestrator = ConversationOrchestrator(db)
    return await orchestrator.process_message_http(
        conversation_id=request.conversation_id,
        message_text=request.message,
        voice_id=request.voice_id,
        speed=request.speed,
        user_id=request.user_id,
    )


@router.get("/conversation/{id}", response_model=ConversationResponse)
async def get_conversation(id: str, db: AsyncSession = Depends(get_db)):
    """Fetch conversation metadata by ID."""
    repo = ConversationRepository(db)
    conv = await repo.get_by_id(id)
    if not conv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
    return ConversationResponse(
        id=conv.id,
        user_id=conv.user_id,
        learning_language=conv.learning_language,
        native_language=conv.native_language,
        difficulty=conv.difficulty,
        voice_id=conv.voice_id,
        speed=conv.speed,
        title=conv.title,
        created_at=conv.created_at,
        updated_at=conv.updated_at,
    )


@router.get("/conversation/{id}/messages", response_model=List[MessageResponse])
async def get_conversation_messages(id: str, limit: int = 50, db: AsyncSession = Depends(get_db)):
    """Fetch message history for a conversation."""
    repo = MessageRepository(db)
    messages = await repo.get_conversation_history(id, limit=limit)
    return [
        MessageResponse(
            id=m.id,
            conversation_id=m.conversation_id,
            role=m.role,
            text=m.text,
            language=m.language,
            sequence_number=m.sequence_number,
            created_at=m.created_at,
        )
        for m in messages
    ]
