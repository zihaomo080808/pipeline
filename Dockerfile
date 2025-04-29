FROM apache/airflow:2.5.1-python3.8

# 1) Copy in your requirements.txt first
COPY requirements.txt .

# 2) Switch to the 'airflow' user before running pip install
USER airflow

# 3) Install all extras as airflow
RUN pip install --no-cache-dir psycopg2-binary -r requirements.txt

# 4) Back to root to copy the rest of your code
USER root

# 5) Copy your files into the image
# No need to copy dags or src since we're mounting them as volumes

# 6) Ensure airflow owns everything in /opt/airflow
RUN chown -R airflow: /opt/airflow

# 7) Switch back to the airflow user for runtime
USER airflow
# ────────────────────────────────────────────────────────────────────────────────
