# app/api/ask.py
from fastapi import APIRouter, HTTPException
import os, json
from app.services.llm_client import GeminiClient

router = APIRouter()
DATA_DIR = "data/texts"

@router.post("/")
async def ask(document_id: str, question: str):
    """
    Ask endpoint: Ask a question about a specific document.
    """
    text_path = os.path.join(DATA_DIR, f"{document_id}.json")

    if not os.path.exists(text_path):
        raise HTTPException(status_code=404, detail="Document not found")

    # Load previously extracted text
    with open(text_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    full_text = "\n".join(data["pages"])

    # Initialize Gemini mock client
    gemini = GeminiClient()

    # Create a mock "prompt" for now (later we'll send to Gemini API)
    prompt = f"Question: {question}\n\nText:\n{full_text}"

    # Get AI-generated (mock) answer
    answer = gemini.answer_question(prompt)

    return {
        "document_id": document_id,
        "question": question,
        "answer": answer
    }
