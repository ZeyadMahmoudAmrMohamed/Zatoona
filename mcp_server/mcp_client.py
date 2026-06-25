import os
from schemas.note_chunk import NoteChunk
from config.settings import MCP_HOST, MCP_PORT

USE_REAL_MCP = os.getenv("USE_REAL_MCP", "false").lower() == "true"

def get_chunk_by_id(chunk_id: str) -> NoteChunk | None:
    if USE_REAL_MCP:
        return _real_get_chunk_by_id(chunk_id)
    else:
        return _mock_get_chunk_by_id(chunk_id)

# ── mock ─────────────────────────────────────────────────────
def _mock_get_chunk_by_id(chunk_id: str) -> NoteChunk | None:
    from tests.team_c.mock_mcp_tool import get_chunk_by_id as mock
    return mock(chunk_id)

# ── real (Team A MCP server) ──────────────────────────────────
def _real_get_chunk_by_id(chunk_id: str) -> NoteChunk | None:
    import httpx
    url = f"http://{MCP_HOST}:{MCP_PORT}/mcp"
    payload = {
        "method": "tools/call",
        "params": {
            "name": "get_chunk_by_id",
            "arguments": {"chunk_id": chunk_id}
        }
    }
    response = httpx.post(url, json=payload)
    response.raise_for_status()
    data = response.json()

    # extract result from MCP response
    result = data.get("result", {})
    content = result.get("content", [])
    if not content:
        return None

    import json
    chunk_data = json.loads(content[0]["text"])
    return NoteChunk(**chunk_data)