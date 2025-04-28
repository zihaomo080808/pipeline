from src.db     import SessionLocal
from src.models import RawOpportunity, Opportunity
from src.transform.clean import RawOpp, clean_payload
from datetime import datetime

def upsert_opportunities():
    db = SessionLocal()
    raws = db.query(RawOpportunity).all()
    for raw in raws:
        clean = clean_payload(RawOpp(raw_payload=raw.raw_payload))
        db.merge(Opportunity(
            title       = clean.title,
            description = clean.description,
            what        = clean.what,
            when_at     = clean.when_at,
            where_city  = clean.where_city,
            who         = clean.who,
            skills      = clean.skills,
            topic_tags  = clean.topic_tags,
            source_url  = str(clean.source_url),
            created_at  = raw.ingested_at
        ))
    db.commit()
    db.close()
