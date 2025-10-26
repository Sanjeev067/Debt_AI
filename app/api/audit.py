# app/api/audit.py
from fastapi import APIRouter, HTTPException
import os, json, re

router = APIRouter()
DATA_DIR = "data/texts"

@router.post("/")
async def audit(document_id: str):
    """
    Audit endpoint: analyze contract text and flag risky clauses.
    """
    text_path = os.path.join(DATA_DIR, f"{document_id}.json")
    if not os.path.exists(text_path):
        raise HTTPException(status_code=404, detail="Document not found")

    with open(text_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    full_text = " ".join(data["pages"]).lower()

    findings = []

    # 1️⃣ Check for short termination notice (<30 days)
    match = re.search(r"(\d+)\s+day[s]?\s+notice", full_text)
    if match:
        days = int(match.group(1))
        if days < 30:
            findings.append({
                "issue": "Short termination notice period",
                "severity": "HIGH",
                "evidence": f"{days} days notice found"
            })
    else:
        findings.append({
            "issue": "No explicit termination notice period found",
            "severity": "MEDIUM"
        })

    # 2️⃣ Check for unlimited liability
    if "unlimited liability" in full_text or "no cap" in full_text:
        findings.append({
            "issue": "Unlimited or no liability cap",
            "severity": "CRITICAL",
            "evidence": "Found phrases like 'unlimited liability' or 'no cap'"
        })

    # 3️⃣ Check for indemnity clause
    if "indemnity" not in full_text:
        findings.append({
            "issue": "Missing indemnity clause",
            "severity": "HIGH"
        })

    # 4️⃣ Check for auto-renewal clause
    if "auto-renew" in full_text or "automatically renew" in full_text:
        findings.append({
            "issue": "Auto-renewal clause present",
            "severity": "MEDIUM",
            "evidence": "Contract may renew automatically unless notice is given"
        })

    if not findings:
        findings.append({
            "issue": "No high-risk clauses detected",
            "severity": "LOW"
        })

    return {
        "document_id": document_id,
        "findings": findings
    }
