import time
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class PipelineMetrics(BaseModel):
    """Timing metrics for monitoring processing latency across pipeline stages."""
    language_detection_ms: float = 0.0
    llm_first_token_ms: float = 0.0
    llm_total_ms: float = 0.0
    grammar_ms: float = 0.0
    tts_first_chunk_ms: float = 0.0
    tts_total_ms: float = 0.0
    total_response_ms: float = 0.0

    def to_dict(self) -> Dict[str, float]:
        return {
            "language_detection_ms": round(self.language_detection_ms, 2),
            "llm_first_token_ms": round(self.llm_first_token_ms, 2),
            "llm_total_ms": round(self.llm_total_ms, 2),
            "grammar_ms": round(self.grammar_ms, 2),
            "tts_first_chunk_ms": round(self.tts_first_chunk_ms, 2),
            "tts_total_ms": round(self.tts_total_ms, 2),
            "total_response_ms": round(self.total_response_ms, 2),
        }


class Timer:
    """Utility class to measure execution duration in milliseconds."""
    def __init__(self):
        self.start_time: Optional[float] = None
        self.elapsed_ms: float = 0.0

    def __enter__(self):
        self.start_time = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time is not None:
            self.elapsed_ms = (time.perf_counter() - self.start_time) * 1000.0
