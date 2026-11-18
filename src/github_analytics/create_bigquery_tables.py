import logging
import os

from dotenv import load_dotenv
from google.cloud import bigquery

load_dotenv()

logger = logging.getLogger(__name__)

DATASET = "raw"
LOCATION = "US"  # a dataset's location cannot be changed later


def payload_schema(key_name, key_type):
    return [
        bigquery.SchemaField("repo", "STRING", mode="REQUIRED"),
        bigquery.SchemaField(key_name, key_type, mode="REQUIRED"),
        bigquery.SchemaField("batch_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("extracted_at", "TIMESTAMP", mode="REQUIRED"),
        bigquery.SchemaField("loaded_at", "TIMESTAMP", mode="REQUIRED"),
        bigquery.SchemaField("payload", "STRING", mode="REQUIRED"),
    ]


TABLES = {
    "repo_snapshots": {
        "schema": [
            bigquery.SchemaField("repo_id", "INT64", mode="REQUIRED"),
            bigquery.SchemaField("repo", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("snapshot_date", "DATE", mode="REQUIRED"),
            bigquery.SchemaField("stars", "INT64"),
            bigquery.SchemaField("forks", "INT64"),
            bigquery.SchemaField("open_issues", "INT64"),
            bigquery.SchemaField("watchers", "INT64"),
            bigquery.SchemaField("loaded_at", "TIMESTAMP", mode="REQUIRED"),
        ],
        "partition_field": "snapshot_date",
    },
    "repositories": {
        "schema": [
            bigquery.SchemaField("repo", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("batch_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("extracted_at", "TIMESTAMP", mode="REQUIRED"),
            bigquery.SchemaField("loaded_at", "TIMESTAMP", mode="REQUIRED"),
            bigquery.SchemaField("payload", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("languages", "STRING"),
        ],
        "partition_field": "extracted_at",
    },
    "commits": {
        "schema": payload_schema("sha", "STRING"),
        "partition_field": "extracted_at",
    },
    "issues": {
        "schema": payload_schema("number", "INT64"),
        "partition_field": "extracted_at",
    },
    "pull_requests": {
        "schema": payload_schema("number", "INT64"),
        "partition_field": "extracted_at",
    },
}


def main():
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    project_id = os.getenv("GCP_PROJECT_ID")
    client = bigquery.Client(project=project_id)

    dataset = bigquery.Dataset(f"{project_id}.{DATASET}")
    dataset.location = LOCATION
    client.create_dataset(dataset, exists_ok=True)
    logger.info("Dataset ready: %s.%s", project_id, DATASET)

    for name, spec in TABLES.items():
        table = bigquery.Table(f"{project_id}.{DATASET}.{name}", schema=spec["schema"])
        table.time_partitioning = bigquery.TimePartitioning(
            type_=bigquery.TimePartitioningType.DAY,
            field=spec["partition_field"],
        )
        table.clustering_fields = ["repo"]
        client.create_table(table, exists_ok=True)
        logger.info("Table ready: %s", name)


if __name__ == "__main__":
    main()