import os

from dotenv import load_dotenv
from google.cloud import bigquery

load_dotenv()

client = bigquery.Client(project=os.getenv("GCP_PROJECT_ID"))
rows = client.query("SELECT 1 AS ok").result()

for row in rows:
    print("Connected to BigQuery, result:", row.ok)