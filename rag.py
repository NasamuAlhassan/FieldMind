import os
from typing import Any, Dict

import chromadb
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

MODEL_NAME = "gemini-2.0-flash"

_client = chromadb.PersistentClient(path="./chroma_db/")
_collection = _client.get_or_create_collection(name="field_reports")


def _get_model() -> genai.GenerativeModel:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not set. Please add it to your .env file.")
    genai.configure(api_key=api_key)
    return genai.GenerativeModel(MODEL_NAME)


def add_report_to_rag(report_id: str, summary: str, metadata: Dict[str, Any]) -> None:
    rag_metadata = {
        "location": str(metadata.get("location", "")),
        "urgency": str(metadata.get("urgency", "")),
        "issue_type": str(metadata.get("issue_type", "")),
        "sentiment": str(metadata.get("sentiment", "")),
    }
    _collection.upsert(
        ids=[str(report_id)],
        documents=[summary or ""],
        metadatas=[rag_metadata],
    )


def query_agent(question: str) -> str:
    if get_report_count() == 0:
        return "No reports are indexed yet. Submit field reports first to enable intelligence querying."

    results = _collection.query(query_texts=[question], n_results=5)
    docs = results.get("documents", [[]])[0]
    metas = results.get("metadatas", [[]])[0]

    context_parts = []
    for i, doc in enumerate(docs):
        metadata = metas[i] if i < len(metas) else {}
        context_parts.append(
            f"Report {i + 1}: {doc} | location={metadata.get('location', '')} | "
            f"urgency={metadata.get('urgency', '')} | issue_type={metadata.get('issue_type', '')} | "
            f"sentiment={metadata.get('sentiment', '')}"
        )

    context = "\n".join(context_parts)
    prompt = f"""
You are FieldMind, an enterprise AI operations agent.
Using the report context below, answer the manager's question with:
1) key patterns,
2) urgency hotspots,
3) concrete recommended actions.

Question:
{question}

Context:
{context}
"""

    model = _get_model()
    response = model.generate_content(prompt)
    return response.text.strip() if response and response.text else "No response generated."


def get_report_count() -> int:
    return int(_collection.count())
