import feedparser
from src.db     import SessionLocal
from src.models import RawOpportunity

FEED_URL = "https://www.eventbrite.com/rss/tag/hackathons/"

def fetch_eventbrite():
    feed = feedparser.parse(FEED_URL)
    db   = SessionLocal()
    for entry in feed.entries:
        db.merge(RawOpportunity(
            source="eventbrite",
            external_id=entry.id,
            raw_payload={
                "title": entry.title,
                "summary": entry.summary,
                "link": entry.link,
                "published": entry.published,
                "id": entry.id
            }
        ))
    db.commit()
    db.close()
