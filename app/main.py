from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
import google.generativeai as genai
import sqlite3
import os
from datetime import datetime
from dotenv import load_dotenv
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
import fitz  # PyMuPDF for reading PDF text

# --- Load environment variables ---
load_dotenv()
genai.configure(api_key=" ")

app = FastAPI()

# --- Allow CORS for frontend access ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- SQLite Database Setup ---
DB_FILE = "summaries.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS summaries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_name TEXT,
            summary TEXT,
            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

def save_summary_to_db(file_name, summary):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO summaries (file_name, summary, created_at) VALUES (?, ?, ?)",
                   (file_name, summary, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()

def get_all_summaries():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT id, file_name, summary, created_at FROM summaries ORDER BY id DESC")
    data = cursor.fetchall()
    conn.close()
    return [{"id": row[0], "file_name": row[1], "summary": row[2], "created_at": row[3]} for row in data]


@app.get("/")
def root():
    return {"message": "FastAPI with SQLite & Gemini API running successfully!"}


# ✅ Step 18: Upload & summarize PDF
@app.post("/uploadfile/")
async def upload_file(file: UploadFile = File(...)):
    try:
        os.makedirs("uploads", exist_ok=True)
        file_path = f"uploads/{file.filename}"

        with open(file_path, "wb") as f:
            f.write(await file.read())

        # Extract text from PDF
        pdf_text = ""
        with fitz.open(file_path) as doc:
            for page in doc:
                pdf_text += page.get_text()

        if not pdf_text.strip():
            return JSONResponse({"status": "error", "message": "No text found in PDF"})

        # Summarize using Gemini
        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(f"Summarize this text briefly and clearly:\n{pdf_text[:15000]}")
        summary = response.text.strip()

        # Save to DB
        save_summary_to_db(file.filename, summary)

        return JSONResponse({"status": "ok", "file_name": file.filename, "summary": summary})

    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)})


# ✅ Step 19: Retrieve all summaries
@app.get("/get_summaries/")
async def get_summaries():
    data = get_all_summaries()
    return JSONResponse({"status": "ok", "results": data})


# ✅ Step 20: Export AI Summary as a PDF report
@app.post("/download_pdf/")
async def download_pdf(file_name: str = Form(...), summary: str = Form(...)):
    try:
        os.makedirs("downloads", exist_ok=True)
        pdf_path = f"downloads/{file_name}_summary.pdf"

        c = canvas.Canvas(pdf_path, pagesize=A4)
        width, height = A4

        # Header
        c.setFont("Helvetica-Bold", 16)
        c.drawString(1 * inch, height - 1 * inch, "AI Summary Report")

        c.setFont("Helvetica", 12)
        c.drawString(1 * inch, height - 1.3 * inch, f"File: {file_name}")
        c.drawString(1 * inch, height - 1.6 * inch, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # Add summary text
        c.setFont("Helvetica", 11)
        text_obj = c.beginText(1 * inch, height - 2.2 * inch)
        text_obj.setLeading(15)
        lines = summary.split("\n")

        for line in lines:
            for chunk in [line[i:i+90] for i in range(0, len(line), 90)]:
                text_obj.textLine(chunk)

        c.drawText(text_obj)
        c.showPage()
        c.save()

        return FileResponse(pdf_path, filename=f"{file_name}_summary.pdf")

    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)})


# ✅ Step 21: Delete a summary
@app.delete("/delete_summary/{file_name}")
async def delete_summary(file_name: str):
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM summaries WHERE file_name=?", (file_name,))
        conn.commit()
        conn.close()
        return JSONResponse({"status": "ok", "message": f"{file_name} deleted successfully"})
    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)})

