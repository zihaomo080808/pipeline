"""
RSS Ingest Pipeline DAG

This DAG fetches data from various RSS feeds using the eventbrite module,
transforms the data, and loads it into the database on an hourly schedule.
"""

from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import sys
import os
import logging

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from src.ingest.eventbrite import fetch_eventbrite
from src.load.to_postgres import upsert_opportunities

# Configure logging
logger = logging.getLogger(__name__)

default_args = {
    "owner": "you",
    "depends_on_past": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
    "start_date": datetime(2025, 4, 1),
    "catchup": False
}

with DAG(
    dag_id="rss_ingest_pipeline",
    default_args=default_args,
    schedule_interval="@hourly",
    tags=["ingest", "rss"],
    doc_md=__doc__
) as dag:
    
    # Task to fetch data from RSS feeds
    fetch_rss = PythonOperator(
        task_id="fetch_rss_feeds",
        python_callable=fetch_eventbrite,
        on_failure_callback=lambda context: logger.error(
            f"RSS feed fetch failed: {context.get('exception')}"
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
    fetch_rss >> transform_load