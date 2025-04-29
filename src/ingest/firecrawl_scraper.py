"""
Firecrawl Scraper Module

Uses the Firecrawl API to crawl websites for opportunities and ingest them
into the raw_opportunities table.
"""

import os
import json
import requests
from dotenv import load_dotenv
from datetime import datetime
from src.db import SessionLocal
from src.models import RawOpportunity

# Load environment variables
load_dotenv()

def ingest_firecrawl(root_urls=None):
    """
    Crawl specified websites using Firecrawl API and ingest results into the database.
    
    Args:
        root_urls (list): List of root URLs to start crawling from.
                         If None, uses default URLs.
    
    Returns:
        int: Number of opportunities ingested
    """
    # Get API key from environment
    api_key = os.getenv("FIRECRAWL_API_KEY")
    if not api_key:
        print("[ERROR] FIRECRAWL_API_KEY environment variable not set")
        return 0
        
    # Use provided URLs or default to empty list
    urls_to_crawl = root_urls or []
    
    if not urls_to_crawl:
        print("[WARN] No URLs provided for crawling")
        return 0
    
    # Initialize database session
    db = SessionLocal()
    count = 0
    
    try:
        # Call Firecrawl API for each root URL
        for url in urls_to_crawl:
            print(f"[INFO] Crawling {url}")
            
            try:
                # Make API request to Firecrawl
                response = requests.post(
                    "https://api.firecrawl.com/v1/crawl",
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "url": url,
                        "max_depth": 2,
                        "follow_links": True,
                        "extract_rules": {
                            "title": "h1, .event-title, .opportunity-title, .title",
                            "description": ".description, .event-description, article p, .summary",
                            "date": ".date, .event-date, time",
                            "location": ".location, .venue, .event-location",
                            "link": "canonical, og:url"
                        }
                    },
                    timeout=30
                )
                
                response.raise_for_status()
                crawl_results = response.json().get("results", [])
                
                # Process and store each result
                for result in crawl_results:
                    # Skip if missing required fields
                    if not result.get("title") or not result.get("link"):
                        continue
                        
                    # Create payload with available data
                    opportunity_data = {
                        "title": result.get("title", ""),
                        "summary": result.get("description", ""),
                        "link": result.get("link", ""),
                        "published": result.get("date", datetime.utcnow().isoformat()),
                        "location": result.get("location")
                    }
                    
                    # Insert into database using merge for idempotency
                    db.merge(RawOpportunity(
                        source="firecrawl",
                        external_id=result.get("link"),  # URL as unique identifier
                        raw_payload=opportunity_data
                    ))
                    
                    count += 1
                    
            except requests.RequestException as e:
                print(f"[ERROR] Failed to crawl {url}: {str(e)}")
                continue
                
        # Commit all changes
        db.commit()
        print(f"[INFO] Successfully ingested {count} opportunities from web crawling")
        return count
        
    except Exception as e:
        print(f"[ERROR] Unexpected error during crawl ingest: {str(e)}")
        db.rollback()
        return 0
        
    finally:
        db.close()

if __name__ == "__main__":
    # Example URLs for testing
    test_urls = [
        "https://devpost.com/hackathons",
        "https://mlh.io/events"
    ]
    
    ingest_firecrawl(test_urls)