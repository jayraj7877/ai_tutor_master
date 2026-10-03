# AI English Tutor SaaS Backend

A production-ready, clean modular Python backend built with FastAPI, SQLAlchemy 2.0 (async), Redis, and Alembic for an AI English Tutor SaaS platform.

Designed to serve mobile (Android) clients with real-time text-to-conversed-audio progressive streaming and non-blocking grammar analysis.

---

## Key Features & Architecture

- **Clean Modular Provider Abstraction**:
  - **Language Detection Provider**: Identifies primary language, secondary languages, and Hinglish/mixed inputs.
  - **LLM Provider**: Abstract adapter interface for OpenAI, Gemini, Ollama, or local mock generators.
  - **Grammar Engine Provider**: Independent concurrent analysis checking tense mismatch, subject-verb agreement, and phraseology without blocking audio streaming.
  - **TTS Provider**: Abstract adapter supporting gTTS, ElevenLabs, Kokoro, Piper, and synthetic mock audio generators.
- **Concurrent Streaming Pipeline**:
  - Sentences are intelligently chunked using natural boundaries (`TextChunker`).
  - Audio chunks are generated and streamed via WebSocket / HTTP as soon as available with 1-indexed sequence numbers.
- **High Concurrency & SaaS Scalability**:
  - Fully asynchronous non-blocking event loops using Python `asyncio`, `asyncpg`, `httpx`, and `redis.asyncio`.
  - Stateless API service designed for horizontal scaling across worker nodes.
- **Database & Migrations**: PostgreSQL with SQLAlchemy 2.0 async models and Alembic versioned migrations.

---

## Project Structure

```
.
├── app/
│   ├── api/
│   │   └── v1/                # REST endpoints and WebSocket handlers
│   ├── core/                  # Config, DB, Redis, Logging, Metrics, Security
│   ├── models/                # SQLAlchemy database models (User, Conversation, Message, etc.)
│   ├── schemas/               # Pydantic V2 request/response schemas
│   ├── repositories/          # Data access repositories
│   ├── services/              # Text chunker, Context manager
│   ├── providers/             # Swappable Provider Adapters
│   │   ├── language/          # FastLanguageDetector (EN, HI, Hinglish)
│   │   ├── grammar/           # RuleAndLLMGrammarProvider
│   │   ├── llm/               # MockLLM, OpenAI, Gemini
│   │   └── tts/               # gTTS, ElevenLabs, MockTTS
│   ├── orchestrator/          # ConversationOrchestrator pipeline
│   └── main.py                # FastAPI application entry point
├── migrations/                # Alembic migration scripts
├── tests/                     # Automated unit and integration test suite
│   ├── unit/
│   └── integration/
├── ANDROID_API.md             # Android integration specification
├── Dockerfile                 # Optimized container build
├── docker-compose.yml         # Container orchestration (API, PostgreSQL, Redis)
├── Makefile                   # Utility commands
└── requirements.txt           # Python dependencies
```

---

## Getting Started

### 1. Local Development (Virtualenv)

```bash
# Clone repository and create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .\.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run test suite
pytest

# Start development server
uvicorn app.main:app --reload --port 8000
```

Access API Documentation:
- Swagger UI: `http://localhost:8000/api/v1/docs`
- Redoc: `http://localhost:8000/api/v1/redoc`

---

### 2. Docker Compose Deployment (Local VPS)

To spin up the complete backend stack including PostgreSQL, Redis, and FastAPI:

```bash
docker compose up -d --build
```

Health Check Verification:
```bash
curl http://localhost:8000/api/v1/health
curl http://localhost:8000/api/v1/ready
```

---

## Future Scaling Architecture (Toward 100k Concurrent Users)

To scale from single VPS to high-concurrency enterprise SaaS:

1. **Stateless API Tier**: Scale FastAPI containers horizontally behind an NGINX / AWS ALB load balancer.
2. **Dedicated Worker Nodes**: Offload TTS synthesis and LLM completion to async background worker pools (Celery / ARQ / NATS) backed by Redis / RabbitMQ queues.
3. **Connection Management**: Utilize Redis Pub/Sub and WebSocket gateways (or AWS API Gateway WebSocket / GCP Cloud Run WebSockets) to maintain state across horizontal nodes.
4. **Database Read Replicas**: Distribute database read traffic using PostgreSQL primary-replica clusters and PgBouncer connection pooling.
