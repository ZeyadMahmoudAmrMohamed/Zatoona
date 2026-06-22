# Classroom Exam Agent — Project Structure

---

## Root Structure

```
classroom-exam-agent/
│
├── .env                        # all API keys and config (never commit this)
├── .env.example                # template showing required env variables
├── .gitignore                  # ignore .env, __pycache__, chroma_db/, etc.
├── requirements.txt            # all python dependencies
├── README.md                   # project overview and setup instructions
├── main.py                     # entry point — starts the full pipeline
│
├── config/
│   └── settings.py             # loads .env and exposes config constants
│
├── mcp_server/                 # TEAM A
├── vector_db/                  # TEAM A
├── agents/                     # TEAM B + TEAM C
├── graph/                      # TEAM B
├── ui/                         # TEAM C
├── schemas/                    # SHARED — all teams
└── tests/                      # SHARED — all teams
```

---

## Team A — Infrastructure

```
mcp_server/
│
├── __init__.py
├── server.py                   # MCP server setup and startup
└── tools/
    ├── __init__.py
    └── retrieval_tool.py       # get_relevant_chunks(topic) tool definition

vector_db/
│
├── __init__.py
├── chroma_client.py            # ChromaDB connection and collection setup
├── embedder.py                 # converts text chunks into vector embeddings
├── ingestion.py                # takes raw notes → chunks → embeds → stores
└── retriever.py                # semantic search logic used by retrieval_tool
```

---

## Team B — Exam Creation

```
agents/
│
├── __init__.py
├── generator_agent.py          # Agent 1 — generates exam from note chunks
└── validator_agent.py          # Agent 2 — validates questions against notes

graph/
│
├── __init__.py
├── exam_graph.py               # LangGraph state machine definition
├── nodes.py                    # each graph node (generate, validate, route)
├── edges.py                    # conditional edges (approve vs reject routing)
└── state.py                    # ExamState definition — shared graph state
```

---

## Team C — Grading and Feedback

```
agents/
│
├── corrector_agent.py          # Agent 3 — grades answers, pulls chunks, gives feedback

ui/
│
├── __init__.py
├── app.py                      # main UI entry point (Streamlit or CLI)
├── pages/
│   ├── upload_page.py          # student uploads notes and topics
│   ├── exam_page.py            # student sees exam and submits answers
│   └── feedback_page.py        # student sees feedback report
└── components/
    ├── question_card.py        # renders a single question
    └── feedback_card.py        # renders per-question feedback result
```

---

## Shared — Schemas

```
schemas/
│
├── __init__.py
├── note_chunk.py               # NoteChunk schema
├── exam_object.py              # ExamObject + Question schema
└── feedback_report.py          # FeedbackReport + QuestionResult schema
```

### Schema definitions

```python
# schemas/note_chunk.py
class NoteChunk:
    chunk_id   : str
    topic      : str
    content    : str
    session_id : str

# schemas/exam_object.py
class Question:
    question_id      : str
    topic            : str
    question         : str
    correct_answer   : str
    source_chunk_id  : str

class ExamObject:
    session_id : str
    topics     : list[str]
    status     : str          # draft | validated
    questions  : list[Question]

# schemas/feedback_report.py
class QuestionResult:
    question_id    : str
    question       : str
    student_answer : str
    is_correct     : bool
    explanation    : str
    source_chunk   : str

class FeedbackReport:
    session_id        : str
    score             : int
    topics_to_review  : list[str]
    encouragement     : str
    results           : list[QuestionResult]
```

---

## Shared — Tests

```
tests/
│
├── __init__.py
│
├── team_a/
│   ├── test_ingestion.py       # test note chunking and embedding
│   ├── test_retriever.py       # test chunk retrieval by topic
│   └── test_mcp_server.py      # test MCP tool response
│
├── team_b/
│   ├── test_generator_agent.py # test exam generation with mock chunks
│   ├── test_validator_agent.py # test validation logic (approve + reject)
│   └── test_exam_graph.py      # test full LangGraph loop
│
└── team_c/
    ├── test_corrector_agent.py # test grading logic and feedback generation
    └── mock_data/
        ├── mock_exam_object.json    # fake exam for testing without Team B
        └── mock_mcp_response.json   # fake MCP chunks for testing without Team A
```

---

## Environment Variables

```
# .env.example

# LLM
OPENAI_API_KEY=your_openai_key_here
MODEL_NAME=gpt-4o

# ChromaDB
CHROMA_PERSIST_DIR=./chroma_db
CHROMA_COLLECTION_NAME=student_notes

# MCP Server
MCP_SERVER_HOST=localhost
MCP_SERVER_PORT=8000

# Session
SESSION_RESET_ON_START=true

# UI
UI_PORT=8501
```

---

## Requirements

```
# requirements.txt

# LLM and agents
langchain
langchain-openai
langchain-community
langgraph
openai

# MCP
mcp

# Vector DB
chromadb

# Embeddings
sentence-transformers

# UI
streamlit

# Schemas and validation
pydantic

# Environment
python-dotenv

# Testing
pytest
```

---

## Config

```python
# config/settings.py

from dotenv import load_dotenv
import os

load_dotenv()

OPENAI_API_KEY       = os.getenv("OPENAI_API_KEY")
MODEL_NAME           = os.getenv("MODEL_NAME", "gpt-4o")
CHROMA_PERSIST_DIR   = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
CHROMA_COLLECTION    = os.getenv("CHROMA_COLLECTION_NAME", "student_notes")
MCP_HOST             = os.getenv("MCP_SERVER_HOST", "localhost")
MCP_PORT             = int(os.getenv("MCP_SERVER_PORT", 8000))
SESSION_RESET        = os.getenv("SESSION_RESET_ON_START", "true") == "true"
UI_PORT              = int(os.getenv("UI_PORT", 8501))
```

---

## Main Entry Point

```python
# main.py

from config.settings import MCP_HOST, MCP_PORT
from mcp_server.server import start_mcp_server
from graph.exam_graph import run_exam_pipeline
from ui.app import start_ui

if __name__ == "__main__":
    start_mcp_server(host=MCP_HOST, port=MCP_PORT)
    start_ui()
```

---

## File Ownership by Team

```
TEAM A owns:
  mcp_server/
  vector_db/
  tests/team_a/

TEAM B owns:
  agents/generator_agent.py
  agents/validator_agent.py
  graph/
  tests/team_b/

TEAM C owns:
  agents/corrector_agent.py
  ui/
  tests/team_c/
  tests/team_c/mock_data/

ALL TEAMS own:
  schemas/           ← agree on this first before writing anything
  requirements.txt   ← each team adds their dependencies
  .env.example       ← each team adds their required variables
  README.md          ← each team documents their module
```

---

## Setup Instructions

```
# 1. clone the repo
git clone https://github.com/your-team/classroom-exam-agent
cd classroom-exam-agent

# 2. create virtual environment
python -m venv venv
source venv/bin/activate        # mac / linux
venv\Scripts\activate           # windows

# 3. install dependencies
pip install -r requirements.txt

# 4. set up environment variables
cp .env.example .env
# open .env and fill in your API keys

# 5. run the project
python main.py
```

---

## Git Branch Strategy

```
main              ← stable, working code only
  │
  ├── team-a      ← Team A working branch
  ├── team-b      ← Team B working branch
  └── team-c      ← Team C working branch (your branch)

Rule: never push directly to main
      open a pull request and get one review before merging
```

