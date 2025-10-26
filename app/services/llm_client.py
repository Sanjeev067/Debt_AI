# app/services/llm_client.py
import json
import os

class GeminiClient:
    """
    Mock Gemini AI client.
    Replace this later with actual Gemini API integration.
    """

    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")

    def extract_contract_data(self, text: str) -> dict:
        """
        For now, return dummy extracted data so the endpoint works.
        """
        # Later, you’ll call Gemini’s API here and parse the JSON.
        return {
            "parties": ["Company A", "Company B"],
            "effective_date": "2024-01-01",
            "term": "2 years",
            "governing_law": "California",
            "payment_terms": "30 days from invoice",
            "termination": "Either party with 60 days notice",
            "auto_renewal": "Yes",
            "confidentiality": "Mutual",
            "indemnity": "Standard clause",
            "liability_cap": "$100,000",
            "signatories": ["John Doe", "Jane Smith"]
        }
    def answer_question(self, prompt: str) -> str:
        """
        For now, return a mock answer.
        Later, connect to Gemini AI API to get real answers.
        """
        # This is a simple simulated answer based on keywords
        q = prompt.lower()
        if "termination" in q:
            return "The termination clause allows either party to terminate with 60 days notice."
        elif "payment" in q:
            return "Payments must be made within 30 days of receiving an invoice."
        elif "law" in q or "governing" in q:
            return "The contract is governed by the laws of California."
        else:
            return "This is a mock AI response. Please integrate Gemini for real answers."
