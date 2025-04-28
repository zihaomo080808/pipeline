from pydantic import BaseModel, HttpUrl, validator
from datetime import datetime

class RawOpp(BaseModel):
    raw_payload: dict

class CleanOpp(BaseModel):
    title: str
    description: str
    what: str
    when_at: datetime | None
    where_city: str | None
    who: str | None
    skills: list[str]
    topic_tags: list[str]
    source_url: HttpUrl

def clean_payload(raw: RawOpp) -> CleanOpp:
    data = raw.raw_payload
    # map fields however your source defines them:
    return CleanOpp(
        title=data.get("title", ""),
        description=data.get("summary", ""),
        what="event" if "event" in data.get("summary","").lower() else "opportunity",
        when_at=datetime.fromisoformat(data.get("published")) if data.get("published") else None,
        where_city=data.get("city"),
        who=data.get("organizer"),
        skills=data.get("skills", []),
        topic_tags=data.get("tags", []),
        source_url=data.get("link") or data.get("url")
    )
