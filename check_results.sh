To check new browser scrape results, run this command:
python -c "
import sqlite3
import os

# Connect to SQLite database
conn = sqlite3.connect('oppradar.db')
cursor = conn.cursor()

# Check for browser scraper data
cursor.execute(\"SELECT source, COUNT(*) FROM raw_opportunities WHERE source = 'browseruse'\")
result = cursor.fetchone()

if result and result[1] > 0:
    print(f\"Browser scraping successful\! Found {result[1]} records.\")
    
    # Show a sample of the results
    cursor.execute(\"\"\"
        SELECT 
            ro.source,
            ro.external_id,
            ro.raw_payload,
            ro.ingested_at
        FROM raw_opportunities ro
        WHERE ro.source = 'browseruse'
        ORDER BY ro.ingested_at DESC
        LIMIT 3
    \"\"\")
    
    rows = cursor.fetchall()
    for i, row in enumerate(rows):
        print(f\"\nResult #{i+1}:\")
        try:
            import json
            payload = json.loads(row[2])
            if 'title' in payload:
                print(f\"Title: {payload['title']}\")
            if 'summary' in payload:
                print(f\"Summary: {payload['summary'][:100]}...\")
            if 'link' in payload:
                print(f\"Link: {payload['link']}\")
        except:
            print(\"Could not parse payload\")
else:
    print(\"No browser scraper data found yet. The scraping job may still be running.\")
    print(\"You can trigger it manually with: AIRFLOW_HOME=/Users/zihaomo/pipeline/airflow_home airflow dags trigger browser_scrape_ingest_pipeline\")

conn.close()
"
