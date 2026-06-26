from config import settings
from schemas.note_chunk import NoteChunk
from vector_db import chroma_client, retriever


def get_relevant_chunks(
    topic: str,
    top_k: int = settings.RETRIEVAL_TOP_K,
    session_id: str | None = None,
) -> list[NoteChunk]:
    session_id = session_id or settings.SESSION_ID
    collection = chroma_client.get_collection(session_id)
    return retriever.search(topic, top_k=top_k, session_id=session_id, collection=collection)


def get_chunk_by_id(chunk_id: str, session_id: str | None = None) -> NoteChunk | None:
    session_id = session_id or settings.SESSION_ID
    collection = chroma_client.get_collection(session_id)
    return retriever.get_by_id(chunk_id, session_id=session_id, collection=collection)


def register(mcp):
    mcp.tool()(get_relevant_chunks)
    mcp.tool()(get_chunk_by_id)
