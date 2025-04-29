from pydantic import BaseModel, HttpUrl, validator
from datetime import datetime
from email.utils import parsedate_to_datetime
import re

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

def parse_date(date_str):
    """Parse various date formats to datetime"""
    if not date_str:
        return None
        
    # Try ISO format
    try:
        return datetime.fromisoformat(date_str)
    except ValueError:
        pass
        
    # Try RFC 2822 format (email date format)
    try:
        return parsedate_to_datetime(date_str)
    except:
        pass
    
    # Try simple YYYY-MM-DD format
    try:
        return datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        pass
        
    # Return current time if all else fails
    return datetime.now()

def extract_skills(text):
    """Extract common tech skills from text"""
    if not text:
        return []
        
    skills = []
    tech_keywords = ["python", "javascript", "react", "node", "aws", "cloud", "ai", 
                   "ml", "data science", "blockchain", "web3", "fullstack", "backend",
                   "frontend", "mobile", "devops", "docker", "kubernetes"]
                   
    text_lower = text.lower()
    for keyword in tech_keywords:
        if keyword in text_lower:
            skills.append(keyword)
            
    return skills

def clean_payload(raw: RawOpp) -> CleanOpp:
    data = raw.raw_payload
    
    title = data.get("title", "")
    description = data.get("summary", "")
    combined_text = f"{title} {description}"
    
    # Extract skills from text
    skills = extract_skills(combined_text)
    
    # Extract tags if they exist
    tags = []
    if "tags" in data:
        if isinstance(data["tags"], list):
            for tag in data["tags"]:
                if isinstance(tag, dict) and "term" in tag:
                    tags.append(tag["term"])
                elif isinstance(tag, str):
                    tags.append(tag)
    elif "categories" in data and isinstance(data["categories"], list):
        for category in data["categories"]:
            if isinstance(category, dict) and "term" in category:
                tags.append(category["term"])
            elif isinstance(category, str):
                tags.append(category)
    
    # Determine event type
    event_keywords = ["hackathon", "conference", "meetup", "workshop", "webinar"]
    event_type = "opportunity"
    for keyword in event_keywords:
        if keyword in combined_text.lower():
            event_type = keyword
            break
    
    # Extract possible organizer
    organizer = data.get("author", None) or data.get("organizer", None)
    
    return CleanOpp(
        title=title,
        description=description,
        what=event_type,
        when_at=parse_date(data.get("published")),
        where_city=data.get("city") or data.get("location", None),
        who=organizer,
        skills=skills,
        topic_tags=tags,
        source_url=data.get("link") or data.get("url")
    )
