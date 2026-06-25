import os
os.environ["USE_REAL_MCP"] = "true"

from mcp_server.mcp_client import get_chunk_by_id

def test_real_mcp():
    # ask Team A for any chunk_id that exists in their DB
    chunk = get_chunk_by_id("chunk_001")
    if chunk:
        print(f"Connected! Got chunk: {chunk.chunk_id} — {chunk.content[:50]}")
    else:
        print("Connected but chunk not found — check the chunk_id")

if __name__ == "__main__":
    test_real_mcp()