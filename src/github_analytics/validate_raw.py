import logging
import os
import sys

import load_to_bigquery as loader
from dotenv import load_dotenv
from google.cloud import bigquery

load_dotenv()

logger = logging.getLogger(__name__)


def file_counts():
    stamp = "validation"
    return {
        "repo_snapshots": len(loader.snapshot_rows(stamp)),
        "repositories": len(loader.repository_rows(stamp)),
        "commits": len(loader.item_rows("commits", "sha", stamp)),
        "issues": len(loader.item_rows("issues", "number", stamp)),
        "pull_requests": len(loader.item_rows("pulls", "number", stamp)),
    }


def warehouse_counts(client, project_id, tables):
    counts = {}
    for table in tables:
        query = f"SELECT COUNT(*) AS n FROM `{project_id}.{loader.DATASET}.{table}`"
        counts[table] = next(iter(client.query(query).result())).n
    return counts


def compare_counts(files, warehouse):
    return [
        (table, files[table], warehouse.get(table))
        for table in files
        if files[table] != warehouse.get(table)
    ]


def main():
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    project_id = os.getenv("GCP_PROJECT_ID")
    client = bigquery.Client(project=project_id)

    files = file_counts()
    warehouse = warehouse_counts(client, project_id, files)

    for table in files:
        logger.info("%s: files=%s bigquery=%s", table, files[table], warehouse[table])

    problems = compare_counts(files, warehouse)
    if problems:
        for table, in_files, in_bigquery in problems:
            logger.error("MISMATCH %s: files=%s bigquery=%s", table, in_files, in_bigquery)
        return 1

    logger.info("All row counts match")
    return 0


if __name__ == "__main__":
    sys.exit(main())