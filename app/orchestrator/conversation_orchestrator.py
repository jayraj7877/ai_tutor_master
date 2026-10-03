import time
import base64
import asyncio
from typing import AsyncGenerator, Dict, Any, Optional, List
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import logger
from app.core.metrics import PipelineMetrics
from app.repositories.conversation_repo import ConversationRepository
from app.repositories.message_repo import MessageRepository
from app.repositories.grammar_repo import GrammarRepository
from app.services.text_chunker import TextChunker
from app.services.context_manager import ConversationContextManager
from app.providers.language.factory import get_language_detection_provider
from app.providers.grammar.factory import get_grammar_provider
from app.providers.llm.factory import get_llm_provider
from app.providers.tts.factory import get_tts_provider
from app.schemas.conversation import ConversationMessageResponse, AudioChunkSchema
from app.schemas.grammar import GrammarAnalysisResult
from app.schemas.websocket import WSOutgoingEvent


class ConversationOrchestrator:
    """Orchestrates concurrent pipeline: Language Detection, LLM, Grammar Engine, Text Chunking, and TTS."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.conv_repo = ConversationRepository(db)
        self.msg_repo = MessageRepository(db)
        self.grammar_repo = GrammarRepository(db)
        self.text_chunker = TextChunker()
        self.context_manager = ConversationContextManager()

        self.lang_provider = get_language_detection_provider()
        self.grammar_provider = get_grammar_provider()
        self.llm_provider = get_llm_provider()
        self.tts_provider = get_tts_provider()

    async def process_message_http(
        self,
        conversation_id: str,
        message_text: str,
        voice_id: str = "female_01",
        speed: float = 0.95,
        user_id: Optional[str] = None,
    ) -> ConversationMessageResponse:
        """Processes user message synchronously/aggregated for HTTP client while keeping internal concurrency."""
        pipeline_start = time.perf_counter()
        metrics = PipelineMetrics()

        # Step 1: Language Detection
        t_lang_start = time.perf_counter()
        lang_res = await self.lang_provider.detect(message_text)
        metrics.language_detection_ms = (time.perf_counter() - t_lang_start) * 1000.0

        # Step 2: Ensure Conversation exists & Store User Message
        conv = await self.conv_repo.get_or_create(
            conversation_id=conversation_id,
            user_id=user_id,
            voice_id=voice_id,
            speed=speed,
        )
        user_msg_db = await self.msg_repo.add_message(
            conversation_id=conversation_id,
            role="user",
            text=message_text,
            language=lang_res.primary_language,
        )

        # Step 3: Trigger Grammar Analysis concurrently
        t_grammar_start = time.perf_counter()
        grammar_task = asyncio.create_task(
            self.grammar_provider.analyze(message_text, language=lang_res.primary_language)
        )

        # Step 4: Fetch Context & Generate LLM Response
        history_db = await self.msg_repo.get_conversation_history(conversation_id, limit=10)
        formatted_history = self.context_manager.format_history_for_llm(
            [{"role": m.role, "text": m.text} for m in history_db],
            learning_language=conv.learning_language,
            difficulty=conv.difficulty,
        )

        t_llm_start = time.perf_counter()
        llm_response = await self.llm_provider.generate_response(
            messages=formatted_history,
            language=lang_res.primary_language,
            conversation_context={"difficulty": conv.difficulty},
        )
        metrics.llm_total_ms = (time.perf_counter() - t_llm_start) * 1000.0
        metrics.llm_first_token_ms = metrics.llm_total_ms / 2.0  # approximate

        # Step 5: Split LLM Response into sentence chunks
        text_chunks = self.text_chunker.split_into_chunks(llm_response.response_text)

        # Step 6: Generate TTS chunks progressively
        audio_chunks: List[AudioChunkSchema] = []
        t_tts_start = time.perf_counter()
        first_chunk_recorded = False

        async for tts_chunk in self.tts_provider.generate_chunks(
            text_chunks=text_chunks,
            voice_id=voice_id,
            language=lang_res.primary_language,
            speed=speed,
        ):
            if not first_chunk_recorded:
                metrics.tts_first_chunk_ms = (time.perf_counter() - t_tts_start) * 1000.0
                first_chunk_recorded = True

            b64_data = base64.b64encode(tts_chunk.data).decode("utf-8")
            audio_chunks.append(
                AudioChunkSchema(
                    sequence=tts_chunk.sequence,
                    format=tts_chunk.format,
                    data=b64_data,
                    text=tts_chunk.text,
                )
            )

        metrics.tts_total_ms = (time.perf_counter() - t_tts_start) * 1000.0

        # Step 7: Await & Persist Grammar mistakes
        grammar_res: GrammarAnalysisResult = await grammar_task
        metrics.grammar_ms = (time.perf_counter() - t_grammar_start) * 1000.0

        if grammar_res.mistakes:
            await self.grammar_repo.save_mistakes(
                conversation_id=conversation_id,
                message_id=user_msg_db.id,
                mistakes=grammar_res.mistakes,
            )

        # Step 8: Save Assistant Response to DB
        await self.msg_repo.add_message(
            conversation_id=conversation_id,
            role="assistant",
            text=llm_response.response_text,
            language=conv.learning_language,
        )

        metrics.total_response_ms = (time.perf_counter() - pipeline_start) * 1000.0

        logger.info(
            "Conversation message processed successfully",
            conversation_id=conversation_id,
            latency_ms=metrics.total_response_ms,
            audio_chunks_count=len(audio_chunks),
        )

        return ConversationMessageResponse(
            conversation_id=conversation_id,
            user_message=message_text,
            assistant_response=llm_response.response_text,
            language_info=lang_res,
            grammar_analysis=grammar_res.mistakes,
            audio_chunks=audio_chunks,
            metrics=metrics.to_dict(),
        )

    async def process_stream_ws(
        self,
        conversation_id: str,
        message_text: str,
        voice_id: str = "female_01",
        speed: float = 0.95,
        user_id: Optional[str] = None,
    ) -> AsyncGenerator[WSOutgoingEvent, None]:
        """Progressively streams events over WebSocket so audio chunks play immediately on Android."""
        yield WSOutgoingEvent(type="conversation_started", conversation_id=conversation_id)

        # Step 1: Language Detection
        lang_res = await self.lang_provider.detect(message_text)
        yield WSOutgoingEvent(
            type="language_detected",
            conversation_id=conversation_id,
            payload=lang_res.model_dump(),
        )

        # Ensure DB setup & save user message
        conv = await self.conv_repo.get_or_create(conversation_id, user_id, voice_id, speed)
        user_msg_db = await self.msg_repo.add_message(conversation_id, "user", message_text, lang_res.primary_language)

        # Step 2: Trigger Grammar Analysis concurrently
        async def run_and_emit_grammar():
            try:
                g_res = await self.grammar_provider.analyze(message_text, lang_res.primary_language)
                if g_res.mistakes:
                    await self.grammar_repo.save_mistakes(conversation_id, user_msg_db.id, g_res.mistakes)
                return g_res
            except Exception as e:
                logger.error("Grammar analysis task failed silently", error=str(e))
                return GrammarAnalysisResult(mistakes=[])

        grammar_task = asyncio.create_task(run_and_emit_grammar())

        # Step 3: Fetch history & generate LLM response
        history_db = await self.msg_repo.get_conversation_history(conversation_id, limit=10)
        formatted_history = self.context_manager.format_history_for_llm(
            [{"role": m.role, "text": m.text} for m in history_db],
            learning_language=conv.learning_language,
            difficulty=conv.difficulty,
        )

        llm_response = await self.llm_provider.generate_response(
            messages=formatted_history,
            language=lang_res.primary_language,
            conversation_context={"difficulty": conv.difficulty},
        )

        # Step 4: Split into text chunks & stream audio chunks immediately
        text_chunks = self.text_chunker.split_into_chunks(llm_response.response_text)
        for idx, text in enumerate(text_chunks, start=1):
            yield WSOutgoingEvent(
                type="text_chunk",
                conversation_id=conversation_id,
                sequence=idx,
                text=text,
            )

        async for tts_chunk in self.tts_provider.generate_chunks(text_chunks, voice_id, lang_res.primary_language, speed):
            b64_data = base64.b64encode(tts_chunk.data).decode("utf-8")
            yield WSOutgoingEvent(
                type="audio_chunk",
                conversation_id=conversation_id,
                sequence=tts_chunk.sequence,
                format=tts_chunk.format,
                data=b64_data,
                text=tts_chunk.text,
            )

        yield WSOutgoingEvent(type="audio_complete", conversation_id=conversation_id)

        # Step 5: Await grammar results and emit
        g_res = await grammar_task
        yield WSOutgoingEvent(
            type="grammar_result",
            conversation_id=conversation_id,
            payload={"mistakes": [m.model_dump() for m in g_res.mistakes]},
        )

        # Save assistant message to DB
        await self.msg_repo.add_message(conversation_id, "assistant", llm_response.response_text, conv.learning_language)

        yield WSOutgoingEvent(type="conversation_complete", conversation_id=conversation_id)
