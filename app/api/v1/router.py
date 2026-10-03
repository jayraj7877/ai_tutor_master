from fastapi import APIRouter
from app.api.v1.health import router as health_router
from app.api.v1.language import router as language_router
from app.api.v1.grammar import router as grammar_router
from app.api.v1.voices import router as voices_router
from app.api.v1.conversation import router as conversation_router
from app.api.v1.websocket import router as websocket_router

api_v1_router = APIRouter()

api_v1_router.include_router(health_router, tags=["Health"])
api_v1_router.include_router(language_router, tags=["Language Detection"])
api_v1_router.include_router(grammar_router, tags=["Grammar Engine"])
api_v1_router.include_router(voices_router, tags=["Voices"])
api_v1_router.include_router(conversation_router, tags=["Conversation"])
api_v1_router.include_router(websocket_router, tags=["WebSocket Streaming"])
