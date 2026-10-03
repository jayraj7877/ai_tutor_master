import logging
import sys
import structlog
from app.core.config import settings

def setup_logging() -> None:
    """Configures structured logging for the application."""
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

    # Standard logging setup for external packages
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=log_level,
    )

    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        sanitize_log_processor,
    ]

    if settings.ENVIRONMENT == "production":
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer(colors=True))

    structlog.configure(
        processors=processors,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


def sanitize_log_processor(logger, method_name, event_dict):
    """Processor to mask secrets and sensitive info in logs."""
    sensitive_keys = {"api_key", "password", "secret", "authorization", "token", "llm_api_key", "tts_api_key"}
    for key in list(event_dict.keys()):
        if any(s_key in key.lower() for s_key in sensitive_keys):
            if isinstance(event_dict[key], str) and event_dict[key]:
                event_dict[key] = event_dict[key][:4] + "..." + event_dict[key][-2:] if len(event_dict[key]) > 8 else "***"
    return event_dict


logger = structlog.get_logger("ai_tutor")
