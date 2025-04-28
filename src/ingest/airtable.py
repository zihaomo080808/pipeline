import requests
from src.db     import SessionLocal
from src.models import RawOpportunity
from src.config import settings

BASE_URL = f"https://api.airtable.com/v0/{settings.AIRTABLE_BASE_ID}/{settings.AIRTABLE_TABLE}"

def fetch_airtable():
    headers = {"Authorization": f"Bearer {settings.AIRTABLE_API_KEY}"}
    resp = requests.get(BASE_URL, headers=headers).json()
    db   = SessionLocal()
    for rec in resp.get("records", []):
        rec_id = rec["id"]
        fields = rec["fields"]
        db.merge(RawOpportunity(
            source="airtable",
            external_id=rec_id,
            raw_payload=fields
        ))
    db.commit()
    db.close()
