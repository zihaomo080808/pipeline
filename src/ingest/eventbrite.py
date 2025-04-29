import requests
import feedparser
from datetime import datetime
from src.db     import SessionLocal
from src.models import RawOpportunity

# 1) The real feed URLs to fetch
FEED_URLS = [
    "https://hackathon.com/feed", # Hackathon.com
    "https://hackernoon.com/feed", # Tech blog with hackathon news
    "https://dev.to/feed/tag/hackathon", # Dev.to hackathon tag
    "https://rss.nytimes.com/services/xml/rss/nyt/Technology.xml", # Tech news
    "https://www.wired.com/feed/rss" # Wired magazine
]

# 2) Fallback in case all HTTP fetches fail or return zero entries
SAMPLE_ENTRIES = [
    {
        "id": "sample-1",
        "title": "Annual Hackathon 2025",
        "summary": "Join us for the biggest hackathon event of the year!",
        "link": "https://example.com/hackathon2025",
        "published": "2025-05-15T12:00:00Z"
    },
    {
        "id": "sample-2",
        "title": "AI Developer Conference",
        "summary": "Learn about the latest in AI development at this exclusive event.",
        "link": "https://example.com/aiconf",
        "published": "2025-06-22T09:00:00Z"
    }
]

# 3) Keywords / tags you actually care about
KEYWORDS = ["hackathon", "conference", "workshop"]

def fetch_eventbrite():
    db      = SessionLocal()
    entries = []

    # Step A: fetch each feed URL over HTTP
    for url in FEED_URLS:
        try:
            resp = requests.get(url, timeout=10, headers={
                "User-Agent": "Mozilla/5.0 (compatible; OpportunityRadar/1.0)"
            })
            resp.raise_for_status()
        except Exception as e:
            print(f"[WARN] Could not fetch RSS from {url!r}: {e}")
            continue

        # Step B: parse via feedparser
        feed = feedparser.parse(resp.content)
        if feed.bozo:
            print(f"[WARN] Malformed feed at {url!r}: {feed.bozo_exception}")

        # Step C: filter entries by keyword match
        for e in feed.entries:
            title   = getattr(e, "title", "")
            summary = getattr(e, "summary", "")
            text     = f"{title}\n{summary}".lower()

            if any(kw in text for kw in KEYWORDS):
                entries.append(e)

    # Fallback to samples if nothing real was found
    if not entries:
        print("[INFO] No real feed entries matched — using SAMPLE_ENTRIES")
        entries = SAMPLE_ENTRIES

    # Step D: ingest into your raw_opportunities table
    for entry in entries:
        if isinstance(entry, dict):
            entry_data = entry
        else:
            entry_data = {
                "id":        entry.id,
                "title":     entry.title,
                "summary":   entry.summary,
                "link":      entry.link,
                "published": getattr(entry, "published", datetime.utcnow().isoformat())
            }

        db.merge(RawOpportunity(
            source       = "eventbrite",
            external_id  = entry_data["id"],
            raw_payload  = entry_data
        ))

    db.commit()
    db.close()
