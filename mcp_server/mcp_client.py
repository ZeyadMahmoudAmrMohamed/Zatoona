import asyncio
import json
import os

from config.settings import MCP_HOST, MCP_PORT
from schemas.note_chunk import NoteChunk

USE_REAL_MCP = os.getenv("USE_REAL_MCP", "false").lower() == "true"


def get_chunk_by_id(chunk_id: str, session_id: str | None = None) -> NoteChunk | None:
    if USE_REAL_MCP:
        return asyncio.run(_real_get_chunk_by_id(chunk_id, session_id))
    from mcp_server.tools.retrieval_tool import get_chunk_by_id as get_chunk_direct

    return get_chunk_direct(chunk_id, session_id=session_id)


async def _real_get_chunk_by_id(chunk_id: str, session_id: str | None = None) -> NoteChunk | None:
    from mcp import ClientSession
    from mcp.client.streamable_http import streamablehttp_client

    url = f"http://{MCP_HOST}:{MCP_PORT}/mcp"
    arguments = {"chunk_id": chunk_id}
    if session_id:
        arguments["session_id"] = session_id

    async with streamablehttp_client(url) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool("get_chunk_by_id", arguments=arguments)
            if not result.content:
                return None
            chunk_data = json.loads(result.content[0].text)
            return NoteChunk(**chunk_data)
