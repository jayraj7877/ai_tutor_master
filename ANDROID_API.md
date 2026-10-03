# Android Integration Contract & API Specification

This document provides complete instructions for Android developers integrating with the AI English Tutor SaaS Backend.

---

## 1. Overview & Architecture Principles

- **Client Input**: The Android application sends **TEXT**, not audio streams.
- **Audio Output**: The backend returns/streams sentence-bounded audio chunks (`mp3` / `wav`).
- **Playback Strategy**: Android maintains an **Audio Playback Queue**. Do NOT wait for the complete response before starting audio playback. Play Chunk 1 immediately, then Chunk 2, Chunk 3 as they arrive.
- **Grammar Feedback**: Grammar corrections are returned as structured data separately. Display them in a feedback card/badge in the UI. Do **not** let grammar checks interrupt spoken conversation.

---

## 2. Audio Playback Queue Protocol

```
Backend WebSocket / HTTP Response
  ├── Chunk 1 (sequence 1) ──> [Android Queue] ──> Play immediately
  ├── Chunk 2 (sequence 2) ──> [Android Queue] ──> Play after Chunk 1 finishes
  └── Chunk 3 (sequence 3) ──> [Android Queue] ──> Play after Chunk 2 finishes
```

---

## 3. Real-Time Streaming via WebSocket (Recommended)

### WebSocket Endpoint:
```
WS /api/v1/conversation/stream
```

### Client Request Frame (JSON):
```json
{
  "action": "send_message",
  "conversation_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "message": "Yesterday I go to market and I meet my friend.",
  "voice_id": "female_01",
  "speed": 0.95
}
```

### Server Event Sequence:

#### 1. `conversation_started`
```json
{
  "type": "conversation_started",
  "conversation_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6"
}
```

#### 2. `language_detected`
```json
{
  "type": "language_detected",
  "conversation_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "payload": {
    "primary_language": "en",
    "confidence": 0.98,
    "detected_languages": ["en"],
    "is_mixed": false
  }
}
```

#### 3. `text_chunk` (Sent as sentence boundaries are split)
```json
{
  "type": "text_chunk",
  "conversation_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "sequence": 1,
  "text": "That sounds like a nice day!"
}
```

#### 4. `audio_chunk` (Sent progressively as audio is synthesized)
```json
{
  "type": "audio_chunk",
  "conversation_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "sequence": 1,
  "format": "mp3",
  "data": "<BASE64_ENCODED_AUDIO_BYTES>",
  "text": "That sounds like a nice day!"
}
```

#### 5. `audio_complete`
```json
{
  "type": "audio_complete",
  "conversation_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6"
}
```

#### 6. `grammar_result` (Emitted independently without blocking audio)
```json
{
  "type": "grammar_result",
  "conversation_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "payload": {
    "mistakes": [
      {
        "original": "I go",
        "corrected": "I went",
        "type": "verb_tense",
        "explanation": "Use past tense 'went' because the action happened in the past."
      },
      {
        "original": "I meet",
        "corrected": "I met",
        "type": "verb_tense",
        "explanation": "Use past tense 'met' for a past encounter."
      }
    ]
  }
}
```

#### 7. `conversation_complete`
```json
{
  "type": "conversation_complete",
  "conversation_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6"
}
```

---

## 4. HTTP REST Endpoints

### 4.1 Send Message (HTTP Alternative)
```
POST /api/v1/conversation/message
```

**Request Headers**: `Content-Type: application/json`

**Request Body**:
```json
{
  "conversation_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "message": "Yesterday I go to market and I meet my friend.",
  "voice_id": "female_01",
  "speed": 0.95
}
```

**Response Body (HTTP 200 OK)**:
```json
{
  "conversation_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "user_message": "Yesterday I go to market and I meet my friend.",
  "assistant_response": "That sounds like a nice day! What did you and your friend do?",
  "language_info": {
    "primary_language": "en",
    "confidence": 0.98,
    "detected_languages": ["en"],
    "is_mixed": false
  },
  "grammar_analysis": [
    {
      "original": "I go",
      "corrected": "I went",
      "type": "verb_tense",
      "explanation": "Use past tense 'went' because the action happened in the past."
    },
    {
      "original": "I meet",
      "corrected": "I met",
      "type": "verb_tense",
      "explanation": "Use past tense 'met' for a past encounter."
    }
  ],
  "audio_chunks": [
    {
      "sequence": 1,
      "format": "mp3",
      "data": "<BASE64_BYTES>",
      "text": "That sounds like a nice day!"
    },
    {
      "sequence": 2,
      "format": "mp3",
      "data": "<BASE64_BYTES>",
      "text": "What did you and your friend do?"
    }
  ],
  "metrics": {
    "language_detection_ms": 2.45,
    "llm_first_token_ms": 120.5,
    "llm_total_ms": 240.1,
    "grammar_ms": 5.12,
    "tts_first_chunk_ms": 45.2,
    "tts_total_ms": 180.4,
    "total_response_ms": 435.6
  }
}
```

---

### 4.2 Get Available Voices
```
GET /api/v1/voices
```

**Response**:
```json
[
  {
    "voice_id": "female_01",
    "name": "Emma (Female - US)",
    "gender": "female",
    "language": "en",
    "sample_url": "https://assets.example.com/voices/female_01.mp3",
    "is_active": true
  },
  {
    "voice_id": "female_02",
    "name": "Priya (Female - Indian/Hinglish)",
    "gender": "female",
    "language": "hi",
    "sample_url": "https://assets.example.com/voices/female_02.mp3",
    "is_active": true
  }
]
```

---

### 4.3 Health & Readiness Checks
- `GET /api/v1/health` -> Returns `{"status": "ok"}`
- `GET /api/v1/ready` -> Returns `{"status": "ready", "database": "ok", "redis": "ok"}`

---

## 5. Voice IDs and Speed Specifications
- Supported `voice_id`: `female_01`, `male_01`, `female_02`, `male_02`.
- `speed`: Float between `0.5` (slow) and `2.0` (fast). Default: `0.95`.
- Language codes: `en` (English), `hi` (Hindi / Hinglish).

---

## 6. Recommended Android ExoPlayer Implementation

1. When receiving an `audio_chunk` event, decode the Base64 `data` string into a temporary audio file or memory buffer.
2. Append the `MediaItem` into ExoPlayer's queue.
3. Call `player.prepare()` and `player.play()` when sequence 1 is enqueued.
4. ExoPlayer will smoothly transition from sequence 1 to sequence 2 without stuttering.
