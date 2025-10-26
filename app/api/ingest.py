# api/ingest.py
from fastapi import APIRouter, UploadFile, File
import fitz  # PyMuPDF
import os
from uuid import uuid4
import json

router = APIRouter()

# Folder to save PDFs and extracted text
BASE_DIR = "data"
PDF_DIR = os.path.join(BASE_DIR, "pdfs")
TEXT_DIR = os.path.join(BASE_DIR, "texts")

os.makedirs(PDF_DIR, exist_ok=True)
os.makedirs(TEXT_DIR, exist_ok=True)

def extract_text_from_pdf(pdf_path: str) -> list[str]:
    """Extracts text from each page of a PDF using PyMuPDF"""
    text_pages = []
    with fitz.open(pdf_path) as doc:
        for page in doc:
            text_pages.append(page.get_text("text"))
    return text_pages


@router.post("/")
async def ingest(files: list[UploadFile] = File(...)):
    """
    Ingest endpoint: Upload one or more PDF files, extract text,
    and save the results.
    """
    saved_docs = []

    for file in files:
        # Generate a unique ID for this document
        doc_id = str(uuid4())
        pdf_path = os.path.join(PDF_DIR, f"{doc_id}.pdf")
        text_path = os.path.join(TEXT_DIR, f"{doc_id}.json")

        # Save uploaded PDF
        with open(pdf_path, "wb") as f:
            f.write(await file.read())

        # Extract text from PDF
        text_pages = extract_text_from_pdf(pdf_path)

        # Save extracted text as JSON
        with open(text_path, "w", encoding="utf-8") as f:
            json.dump({"document_id": doc_id, "pages": text_pages}, f, ensure_ascii=False, indent=2)

        saved_docs.append({
            "document_id": doc_id,
            "filename": file.filename,
            "pdf_path": pdf_path,
            "text_path": text_path,
            "pages": len(text_pages)
        })

    return {"status": "success", "documents": saved_docs}
