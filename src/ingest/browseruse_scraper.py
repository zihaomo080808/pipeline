# src/ingest/browseruse_scraper.py

import os
import json
import asyncio
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from browser_use import Agent

from src.db import SessionLocal
from src.models import RawOpportunity

# 1) Load environment variables from .env
load_dotenv()

# 2) Grab your Browser-Use API key
BROWSER_API_KEY = os.getenv("BROWSER_API_KEY")
if not BROWSER_API_KEY:
    raise RuntimeError("Missing BROWSER_API_KEY in environment — please set it in your .env")

# 3) (Optional) grab your OpenAI API key too, if not already set globally
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("Missing OPENAI_API_KEY in environment")

# 4) Initialize your LLM
llm = ChatOpenAI(model="gpt-4o", openai_api_key=OPENAI_API_KEY)

# 5) List of sites to scrape
TARGET_SITES = [
    # Events & conferences
    "https://www.eventbrite.com",
    "https://www.meetup.com",
    "https://techcrunch.com/events/",
    "https://nips.cc",
    "https://icml.cc",
    "https://cvpr.thecvf.com",
    "https://aaai.org/conference/aaai/",
    "https://london.theaisummit.com",
    "https://newyork.theaisummit.com",
    "https://nvidia.com/gtc/",
    "https://databricks.com/dataaisummit/",
    "https://ai4.io",
    "https://worldsummit.ai",
    "https://collisionconf.com",
    "https://websummit.com",
    "https://allevents.in",
    "https://conferenceindex.org",
    "https://kdnuggets.com/events",
    # Hackathons
    "https://devpost.com",
    "https://mlh.io",
    "https://hackerearth.com/challenges",
    "https://devfolio.co",
    "https://unstop.com",
    "https://angelhack.com",
    "https://hackathon.io",
    # Internships
    "https://www.linkedin.com/jobs/",
    "https://www.indeed.com",
    "https://www.glassdoor.com",
    "https://angel.co/jobs",
    "https://builtin.com",
    # …add any others you listed…
]

async def _crawl_with_agent():
    """
    Uses Browser-Use Agent to visit each TARGET_SITE and return
    a JSON array of {title, summary, link, published}.
    """
    task_prompt = (
        "For each of these domains:\n"
        f"{', '.join(TARGET_SITES)}\n\n"
        "Find all upcoming tech/AI events, hackathons, internships, or opportunities. "
        "Return a JSON array of objects with these keys:\n"
        "  - title (string)\n"
        "  - summary (string, <300 chars)\n"
        "  - link (full URL)\n"
        "  - published (ISO datetime when the listing was posted)\n"
        "Only return valid JSON—no extra commentary."
    )

    # 6) Instantiate Agent with your API key
    # browser-use 0.1.40 expects different parameters
    agent = Agent(
        browser_api_key=BROWSER_API_KEY,
        task=task_prompt,
        llm=llm,
        browser_kwargs={"headless": True}
    )

    raw_output = await agent.run()
    return json.loads(raw_output)

def ingest_browseruse():
    """
    Entrypoint to crawl + upsert into raw_opportunities.
    """
    listings = asyncio.run(_crawl_with_agent())
    db = SessionLocal()
    for item in listings:
        db.merge(RawOpportunity(
            source="browseruse",
            external_id=item["link"],
            raw_payload=item
        ))
    db.commit()
    db.close()
