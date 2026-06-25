import os
import json
import asyncio
from schemas.note_chunk import NoteChunk
from config.settings import MCP_HOST, MCP_PORT

USE_REAL_MCP = os.getenv("USE_REAL_MCP", "false").lower() == "true"

def get_chunk_by_id(chunk_id: str) -> NoteChunk | None:
    if USE_REAL_MCP:
        return asyncio.run(_real_get_chunk_by_id(chunk_id))
    else:
        return _mock_get_chunk_by_id(chunk_id)

# ── mock ─────────────────────────────────────────────────────
def _mock_get_chunk_by_id(chunk_id: str) -> NoteChunk | None:
    from tests.team_c.mock_mcp_tool import get_chunk_by_id as mock
    return mock(chunk_id)

# ── real ─────────────────────────────────────────────────────
async def _real_get_chunk_by_id(chunk_id: str) -> NoteChunk | None:
    from mcp.client.streamable_http import streamablehttp_client
    from mcp import ClientSession

    url = f"http://{MCP_HOST}:{MCP_PORT}/mcp"

    async with streamablehttp_client(url) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool(
                "get_chunk_by_id",
                arguments={"chunk_id": chunk_id}
            )
            if not result.content:
                return None
            chunk_data = json.loads(result.content[0].text)
            return NoteChunk(**chunk_data)