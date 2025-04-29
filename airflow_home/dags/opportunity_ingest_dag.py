from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import sys
import os

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from src.ingest.eventbrite import fetch_eventbrite
from src.ingest.airtable    import fetch_airtable
from src.load.to_postgres    import upsert_opportunities

default_args = {
    'owner': 'you',
    'depends_on_past': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    dag_id="opportunity_pipeline",
    default_args=default_args,
    start_date=datetime(2025, 1, 1),
    schedule_interval="@hourly",
    catchup=False,
) as dag:

    ingest_eventbrite = PythonOperator(
        task_id="ingest_eventbrite",
        python_callable=fetch_eventbrite,
    )

    ingest_airtable = PythonOperator(
        task_id="ingest_airtable",
        python_callable=fetch_airtable,
    )

    load_to_postgres = PythonOperator(
        task_id="transform_and_load",
        python_callable=upsert_opportunities,
    )

    [ingest_eventbrite, ingest_airtable] >> load_to_postgres
