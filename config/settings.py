from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# ── Team C — Corrector Agent (Groq)
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL   = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

# ── Team B — Exam Generator (Lightning AI)
LIGHTNING_API_KEY = os.getenv("LIGHTNING_API_KEY")
BASE_URL          = os.getenv("LIGHTNING_BASE_URL", "https://lightning.ai/api/v1/")
MODEL_NAME_B        = os.getenv("MODEL_NAME_B")
MAX_VALIDATION_ITERATIONS = int(os.getenv("MAX_VALIDATION_ITERATIONS", "3"))
MOCK_MCP_PATH = os.getenv(
    "MOCK_MCP_PATH",
    str(PROJECT_ROOT / "tests" / "team_b" / "mock_data" / "mock_mcp_response.json"),
)

# ── Team A — Vector DB and MCP Server (OpenAI embeddings)
OPENAI_API_KEY         = os.getenv("OPENAI_API_KEY")
EMBEDDING_MODEL        = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
EMBEDDING_PROVIDER     = os.getenv("EMBEDDING_PROVIDER", "auto").lower()
LOCAL_EMBEDDING_MODEL  = os.getenv("LOCAL_EMBEDDING_MODEL", "BAAI/bge-small-en-v1.5")
CHROMA_PERSIST_DIR     = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
CHROMA_COLLECTION      = os.getenv("CHROMA_COLLECTION_NAME", "student_notes")
MCP_HOST               = os.getenv("MCP_SERVER_HOST", "localhost")
MCP_PORT               = int(os.getenv("MCP_SERVER_PORT", "8000"))
RETRIEVAL_TOP_K        = int(os.getenv("RETRIEVAL_TOP_K", "5"))
RETRIEVAL_MODE         = os.getenv("RETRIEVAL_MODE", "hybrid").lower()
RETRIEVAL_CANDIDATE_K  = int(os.getenv("RETRIEVAL_CANDIDATE_K", "20"))
RERANK_ENABLED         = os.getenv("RERANK_ENABLED", "true").lower() == "true"
RERANKER_MODEL         = os.getenv("RERANKER_MODEL", "cross-encoder/ms-marco-MiniLM-L-6-v2")
_min_score             = os.getenv("RERANK_MIN_SCORE", "").strip()
RERANK_MIN_SCORE       = float(_min_score) if _min_score else None
MIN_CHUNK_CHARS        = int(os.getenv("MIN_CHUNK_CHARS", "0"))
SESSION_ID             = os.getenv("SESSION_ID", "default")
SESSION_RESET          = os.getenv("SESSION_RESET_ON_START", "true").lower() == "true"

# ── Shared
UI_PORT    = int(os.getenv("UI_PORT", "8501"))
USE_REAL_MCP     = os.getenv("USE_REAL_MCP", "false").lower() == "true"
USE_REAL_EXAM    = os.getenv("USE_REAL_EXAM", "false").lower() == "true"
USE_REAL_ANSWERS = os.getenv("USE_REAL_ANSWERS", "false").lower() == "true"