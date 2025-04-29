"""
Web Crawl Ingest Pipeline DAG

This DAG runs a daily web crawling job using Firecrawl to ingest opportunities
from configured root URLs. The crawled data is then transformed and loaded
into the database with appropriate throttling to manage resource usage.
"""

from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import sys
import os
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

# Import required modules
from src.ingest.firecrawl_scraper import ingest_firecrawl
from src.load.to_postgres import upsert_opportunities

# Configure logging
logger = logging.getLogger(__name__)

# Root URLs for the crawler to start from
ROOT_URLS = [
    "https://devpost.com/hackathons",
    "https://mlh.io/events",
    "https://www.meetup.com/find/?keywords=tech",
    "https://www.eventbrite.com/d/online/technology-events/",
    "https://techcrunch.com/events/"
]

default_args = {
    "owner": "you",
    "depends_on_past": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=15),
    "start_date": datetime(2025, 4, 1),
    "catchup": False
}

with DAG(
    dag_id="crawl_ingest_pipeline",
    default_args=default_args,
    schedule_interval="@daily",
    max_active_runs=1,
    tags=["ingest", "crawl"],
    doc_md=__doc__
) as dag:
    
    # Task to crawl websites
    crawl_task = PythonOperator(
        task_id="crawl_websites",
        python_callable=ingest_firecrawl,
        op_kwargs={"root_urls": ROOT_URLS},
        pool="crawl_pool",
        on_failure_callback=lambda context: logger.error(
            f"Web crawl failed: {context.get('exception')}"
        )
    )
    
    # Task to transform and load data
    transform_load = PythonOperator(
        task_id="transform_and_load",
        python_callable=upsert_opportunities,
        on_failure_callback=lambda context: logger.error(
            f"Transform and load failed: {context.get('exception')}"
        )
    )
    
    # Set dependencies
    crawl_task >> transform_load