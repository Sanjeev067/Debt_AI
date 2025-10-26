# app/api/extract.py
from fastapi import APIRouter, HTTPException
import os, json
from app.services.llm_client import GeminiClient

router = APIRouter()
DATA_DIR = "data/texts"

@router.post("/")
async def extract(document_id: str):
    """
    Extract structured contract data for a given document ID.
    """
    text_path = os.path.join(DATA_DIR, f"{document_id}.json")

    if not os.path.exists(text_path):
        raise HTTPException(status_code=404, detail="Document not found")

    # Load previously extracted text
    with open(text_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    full_text = "\n".join(data["pages"])

    # Use Gemini mock to extract fields
    gemini = GeminiClient()
    result = gemini.extract_contract_data(full_text)

    return {"document_id": document_id, "extracted_data": result}
