from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import sys, os

# ensure project root is on PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from src.ingest.browseruse_scraper import ingest_browseruse
from src.load.to_postgres import upsert_opportunities

default_args = {
    "owner": "you",
    "depends_on_past": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=15),
}

with DAG(
    dag_id="browser_scrape_ingest_pipeline",
    default_args=default_args,
    start_date=datetime(2025, 4, 1),
    schedule_interval="@daily",
    catchup=False,
    max_active_runs=1,
    tags=["ingest", "browser"],
) as dag:

    scrape = PythonOperator(
        task_id="ingest_browseruse",
        python_callable=ingest_browseruse,
        pool="browser_pool",  # create this pool with 1-2 slots in the Airflow UI
    )

    transform = PythonOperator(
        task_id="transform_after_browser",
        python_callable=upsert_opportunities,
    )

    scrape >> transform
