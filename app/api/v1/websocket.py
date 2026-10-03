import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.logging import logger
from app.orchestrator.conversation_orchestrator import ConversationOrchestrator
from app.schemas.websocket import WSIncomingMessage, WSOutgoingEvent

router = APIRouter()


@router.websocket("/conversation/stream")
async def conversation_stream_endpoint(websocket: WebSocket, db: AsyncSession = Depends(get_db)):
    """Real-time WebSocket endpoint streaming text and audio chunks progressively."""
    await websocket.accept()
    logger.info("WebSocket client connected")

    try:
        while True:
            data_text = await websocket.receive_text()
            try:
                raw_json = json.loads(data_text)
                msg = WSIncomingMessage(**raw_json)
            except Exception as parse_err:
                err_event = WSOutgoingEvent(type="error", error=f"Invalid message format: {str(parse_err)}")
                await websocket.send_text(err_event.model_dump_json(exclude_none=True))
                continue

            orchestrator = ConversationOrchestrator(db)
            try:
                async for event in orchestrator.process_stream_ws(
                    conversation_id=msg.conversation_id,
                    message_text=msg.message,
                    voice_id=msg.voice_id,
                    speed=msg.speed,
                ):
                    await websocket.send_text(event.model_dump_json(exclude_none=True))
            except Exception as stream_err:
                logger.error("Error during WS pipeline execution", error=str(stream_err))
                err_event = WSOutgoingEvent(
                    type="error",
                    conversation_id=msg.conversation_id,
                    error=f"Pipeline error: {str(stream_err)}"
                )
                await websocket.send_text(err_event.model_dump_json(exclude_none=True))

    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected")
    except Exception as e:
        logger.error("Unexpected WebSocket handler exception", error=str(e))
