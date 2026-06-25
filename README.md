# 📚 Leo Agent — Classroom Exam Agent

An end-to-end multi-agent system that transforms a student's raw study material into a personalized, validated exam — then grades the student's answers and returns structured, encouraging feedback.

Built by a team of 6 as part of an Agentic AI course project.

---

## 🧠 What It Does

```
Student uploads notes (PDF, slides, audio, video, YouTube, Notion...)
        │
        ▼
Notes are parsed, chunked, embedded, and stored in a local vector database
        │
        ▼
An exam is generated from the notes and validated for accuracy
        │
        ▼
The student answers the exam through a clean UI
        │
        ▼
Answers are graded by an AI corrector that references the original notes
        │
        ▼
Student receives a detailed feedback report with explanations and encouragement
```

---

## 🏗️ System Architecture

The system is composed of three layers, each built by a dedicated sub-team and connected through shared schemas and a single MCP gateway.

```
┌─────────────────────────────────────────────────────────────┐
│                        STUDENT                              │
│         Uploads notes + topics via UI                       │
└─────────────────────────────┬───────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              LAYER 1 — INFRASTRUCTURE                       │
│                                                             │
│  Raw input (PDF, DOCX, audio, video, YouTube, Notion...)    │
│       │                                                     │
│       ▼                                                     │
│  Parse → Chunk → Embed → Store in ChromaDB (per session)    │
│                              │                              │
│                        MCP Server                           │
│                  (single gateway for all agents)            │
│                              │                              │
│   Tools exposed:                                            │
│     get_relevant_chunks(topic) → NoteChunk[]                │
│     get_chunk_by_id(chunk_id)  → NoteChunk                  │
└─────────────────────────────┬───────────────────────────────┘
                              │
              ┌───────────────┴────────────────┐
              │                                │
              ▼                                ▼
┌─────────────────────────┐      ┌─────────────────────────────┐
│  LAYER 2 — EXAM         │      │  LAYER 3 — GRADING          │
│  CREATION (LangGraph)   │      │  & FEEDBACK                 │
│                         │      │                             │
│  fetch_chunks node      │      │  Student submits answers    │
│       │                 │      │       │                     │
│       ▼                 │      │       ▼                     │
│  Generator Agent        │      │  Corrector Agent            │
│  (drafts exam)          │      │  grades each answer         │
│       │                 │      │  pulls source chunk         │
│       ▼                 │      │  explains mistakes          │
│  Validator Agent ───────┤      │       │                     │
│  (checks grounding)     │      │       ▼                     │
│       │                 │      │  Feedback Report            │
│  ┌────┴────┐            │      │  score + per-question       │
│  │         │            │      │  feedback + encouragement   │
│ REJECT  APPROVE─────────┼──────►  passed to UI              │
│  │                      │      └─────────────────────────────┘
│  └──► loop back         │
│       to generator      │
└─────────────────────────┘
```

---

## ⚙️ Layer 1 — Notes Ingestion & Retrieval

Accepts virtually any input format and turns it into a searchable, session-isolated vector store. The MCP server is the **only** gateway — no other layer touches ChromaDB directly.

### Supported Input Types

```
Files      → PDF, DOCX, PPTX, MD, HTML, images (OCR for scans)
Audio/Video→ MP3, MP4, WAV (transcribed via faster-whisper or Groq ASR)
YouTube    → auto-captions, playlist enumeration, audio fallback
Notion     → page payload normalized to markdown
Web        → opt-in enrichment via web search (off by default)
Plain text → direct ingest
```

### Ingestion Pipeline

```
Raw input
    │
    ├── Document (PDF/DOCX/PPTX/image)
    │       │
    │       └── Docling parser (OCR if scanned)
    │               │
    │               └── HybridChunker (structure-aware)
    │
    ├── Audio / Video
    │       │
    │       └── faster-whisper / Groq ASR → transcript
    │               │
    │               └── Token splitter (with overlap)
    │
    ├── YouTube URL
    │       │
    │       └── Captions → transcript → token splitter
    │
    └── Text / Notion / Web
            │
            └── Direct text → token splitter
                    │
                    ▼
            Embed (OpenAI / local sentence-transformers)
                    │
                    ▼
            Store in ChromaDB (session-isolated collection)
```

### Retrieval Pipeline

```
get_relevant_chunks(topic)
    │
    ├── Dense vector search     ← catches semantic meaning
    ├── BM25 keyword search     ← catches exact terms, names, codes
    ├── RRF fusion              ← merges both rankings
    └── Cross-encoder rerank    ← precision pass
            │
            ▼
    Top-K NoteChunk[] returned to caller
```

### Session Isolation

Each `SESSION_ID` maps to its own ChromaDB directory and client. Two sessions can never see or overwrite each other. `SESSION_RESET_ON_START=true` clears only the bound session on startup.

### NoteChunk — The Cross-Layer Contract

```python
class NoteChunk(BaseModel):
    chunk_id   : str
    topic      : str
    content    : str
    session_id : str
```

Page numbers, slide numbers, headings, and timestamps are kept as internal metadata only and never exposed outside Layer 1.

---

## ⚙️ Layer 2 — Exam Creation (LangGraph)

A self-correcting agentic pipeline that generates exam questions grounded strictly in the student's notes and loops until all questions pass validation.

### Pipeline Flow

```
                    ┌──────────────────────────────────┐
                    │      LANGGRAPH STATE MACHINE      │
                    └───────────┬──────────────────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │   fetch_chunks node   │
                    │   calls MCP server    │
                    │   per topic           │
                    └───────────┬───────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │   Generator Agent     │
                    │                       │
                    │   input:              │
                    │     topics list       │
                    │     note chunks       │
                    │     retry feedback    │
                    │                       │
                    │   output:             │
                    │     ExamObject(draft) │
                    └───────────┬───────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │   Validator Agent     │
                    │                       │
                    │   checks each question│
                    │   is grounded in      │
                    │   referenced chunk    │
                    └───────────┬───────────┘
                                │
               ┌────────────────┴──────────────┐
               │                               │
           REJECT                          APPROVE
    (invalid questions)              (all questions valid)
               │                               │
               ▼                               ▼
    loop back to generator            ExamObject(validated)
    with rejection feedback           passed to Layer 3
    (max 3 iterations)
```

### ExamObject Schema

```python
class Question(BaseModel):
    question_id     : str
    topic           : str
    question        : str
    correct_answer  : str
    source_chunk_id : str   # direct reference to the note chunk

class ExamObject(BaseModel):
    session_id : str
    topics     : list[str]
    status     : Literal["draft", "validated"]
    questions  : list[Question]
```

### Key Features

- Questions are grounded **strictly** in the student's own notes — no external knowledge
- Supports `--difficult` mode: questions synthesize information across multiple chunks
- Self-correction loop replaces only the rejected questions, keeping approved ones
- `--num-questions` controls question count; capped at available chunks if exceeded

---

## ⚙️ Layer 3 — Grading & Feedback

Receives the validated exam and student answers, grades each answer by referencing the original note chunk, and returns a structured feedback report.

### Grading Flow

```
Validated exam + student answers
        │
        ▼
┌───────────────────────────────┐
│      Corrector Agent          │
│                               │
│  for each question:           │
│    get source chunk by ID     │
│    from MCP server            │
│         │                     │
│         ▼                     │
│    grade answer (LLM)         │
│    if wrong:                  │
│      explain using notes      │
│      flag topic for review    │
│                               │
│  generate encouragement msg   │
└───────────────┬───────────────┘
                │
                ▼
┌───────────────────────────────┐
│       Feedback Report         │
│                               │
│  score          e.g. 7/10     │
│  topics_to_review  [...]      │
│  encouragement  "..."         │
│  results[]                    │
│    question                   │
│    student_answer             │
│    is_correct                 │
│    explanation                │
│    source_chunk               │
└───────────────────────────────┘
```

### UI Flow (Streamlit)

```
Page 1 — Exam
  Student sees questions → types answers → submits

Page 2 — Grading
  Spinner shown while corrector agent runs

Page 3 — Feedback Report
  Score + progress bar
  Encouragement message
  Topics to review
  Per-question expandable cards (✅ correct / ❌ wrong + explanation)
  Option to start a new exam
```

---

## 📁 Project Structure

```
Leo-Agent/
│
├── .env                        # API keys and config (never commit)
├── .env.example                # Template — fill and rename to .env
├── requirements.txt            # All dependencies
├── main.py                     # Entry point — starts MCP server + UI
│
├── config/
│   └── settings.py             # Loads .env and exposes all config constants
│
├── agents/
│   ├── generator_agent.py      # Generates exam questions from note chunks
│   ├── validator_agent.py      # Validates questions are grounded in notes
│   ├── corrector_agent.py      # Grades answers and generates feedback
│   ├── exam_loader.py          # Loads exam (mock or real pipeline)
│   └── answer_loader.py        # Loads student answers (mock or real UI)
│
├── graph/
│   ├── exam_graph.py           # LangGraph state machine + run_exam_pipeline()
│   ├── nodes.py                # fetch_chunks, generate, validate nodes
│   ├── edges.py                # Conditional routing (approve vs reject)
│   └── state.py                # ExamState TypedDict
│
├── mcp_server/
│   ├── server.py               # FastMCP app + start_mcp_server()
│   ├── mcp_client.py           # Client used by Layer 3 to call MCP tools
│   └── tools/
│       └── retrieval_tool.py   # get_relevant_chunks(), get_chunk_by_id()
│
├── schemas/
│   ├── note_chunk.py           # NoteChunk — cross-layer contract
│   ├── exam_object.py          # ExamObject, Question, ValidationResult
│   └── feedback_report.py      # FeedbackReport, QuestionResult
│
├── vector_db/
│   ├── ingestion.py            # Router: file/url/text → parse → chunk → store
│   ├── docling_parser.py       # PDF/DOCX/PPTX/images → structured document
│   ├── chunking.py             # HybridChunker / semantic chunking
│   ├── embedder.py             # OpenAI / local embeddings (auto fallback)
│   ├── chroma_client.py        # Per-session ChromaDB client
│   ├── retriever.py            # Hybrid search (dense + BM25 + RRF + rerank)
│   ├── loaders.py              # Audio/video transcription
│   ├── youtube.py              # YouTube captions + playlist + audio fallback
│   ├── notion.py               # Notion page → markdown
│   └── enrichment.py          # Opt-in web enrichment
│
├── ui/
│   └── app.py                  # Streamlit UI (3 pages: exam, loading, report)
│
├── utils/
│   └── report_writer.py        # Save and print feedback reports
│
├── outputs/
│   └── report_<session>.json   # Generated feedback reports
│
└── tests/
    ├── team_a/                 # Ingestion, retrieval, MCP server tests
    ├── team_b/                 # Generator, validator, graph tests
    └── team_c/                 # Corrector agent tests + mock data
```

---

## 🚀 Setup & Running

### 1. Clone and create virtual environment

```bash
git clone https://github.com/your-team/leo-agent.git
cd leo-agent
python -m venv envs/agentic
envs\agentic\Scripts\activate   # Windows
source envs/agentic/bin/activate # Mac/Linux
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment

```bash
cp .env.example .env
# open .env and fill in your API keys
```

Required keys:

```
OPENAI_API_KEY=...        # for embeddings (Layer 1)
LIGHTNING_API_KEY=...     # for exam generation (Layer 2)
GROQ_API_KEY=...          # for grading (Layer 3)
```

### 4. Run the full system

```bash
python main.py
```

This starts the MCP server in the background and launches the Streamlit UI at `http://localhost:8501`.

### 5. Run individual layers

```bash
# Layer 1 — MCP server only
python -m mcp_server.server

# Layer 2 — Exam pipeline CLI
python main.py --session my-session --topics "World War 2,French Revolution"

# Layer 3 — Corrector test
python -m tests.team_c.test_corrector_agent

# UI only
streamlit run ui/app.py
```

---

## 🔧 Configuration

| Key | Default | Description |
|---|---|---|
| `OPENAI_API_KEY` | — | OpenAI key for embeddings |
| `EMBEDDING_PROVIDER` | `auto` | `openai` / `local` / `auto` |
| `LOCAL_EMBEDDING_MODEL` | `BAAI/bge-small-en-v1.5` | Fallback embedding model |
| `CHROMA_PERSIST_DIR` | `./chroma_db` | Vector DB storage path |
| `SESSION_ID` | `default` | Isolates each student session |
| `SESSION_RESET_ON_START` | `true` | Clears session on startup |
| `RETRIEVAL_MODE` | `hybrid` | `hybrid` or `dense` |
| `RETRIEVAL_TOP_K` | `5` | Chunks returned per query |
| `RERANK_ENABLED` | `true` | Cross-encoder reranking |
| `LIGHTNING_API_KEY` | — | Lightning AI key for exam generation |
| `MODEL_NAME` | — | LLM model for exam generation |
| `MAX_VALIDATION_ITERATIONS` | `3` | Max self-correction loops |
| `GROQ_API_KEY` | — | Groq key for answer grading |
| `GROQ_MODEL` | `llama-3.3-70b-versatile` | Groq model for grading |
| `USE_REAL_MCP` | `false` | Switch to real MCP server |
| `USE_REAL_EXAM` | `false` | Switch to real exam pipeline |
| `UI_PORT` | `8501` | Streamlit port |

---

## 🤝 Contributors

This project was built by a team of 6 as part of an Agentic AI course:

| Contributor | GitHub |
|---|---|
| — | — |
| — | — |
| — | — |
| — | — |
| — | — |
| — | — |

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Agent framework | LangChain |
| Orchestration | LangGraph |
| Agent communication | MCP (FastMCP) |
| Vector storage | ChromaDB |
| Embeddings | OpenAI / sentence-transformers |
| Exam generation LLM | Lightning AI |
| Grading LLM | Groq (llama-3.3-70b-versatile) |
| Document parsing | Docling |
| Audio transcription | faster-whisper / Groq ASR |
| UI | Streamlit |
| Validation | Pydantic |
