import json
import logging
import os
from datetime import UTC, datetime
from pathlib import Path

from dotenv import load_dotenv
from google.cloud import bigquery

load_dotenv()

logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = ROOT / "data" / "raw"
DATASET = "raw"


def read_json(path):
    return json.loads(path.read_text())


def batch_id_for(path):
    return path.relative_to(RAW_DIR).as_posix()


def snapshot_rows(loaded_at):
    rows = []
    for path in sorted((RAW_DIR / "repo_snapshots").glob("*/*.json")):
        row = read_json(path)
        row["loaded_at"] = loaded_at
        rows.append(row)
    return rows


def repository_rows(loaded_at):
    rows = []
    for path in sorted((RAW_DIR / "repositories").glob("*/*.json")):
        content = read_json(path)
        rows.append(
            {
                "repo": content["repo"]["full_name"],
                "batch_id": batch_id_for(path),
                "extracted_at": content["extracted_at"],
                "loaded_at": loaded_at,
                "payload": json.dumps(content["repo"]),
                "languages": json.dumps(content["languages"]),
            }
        )
    return rows


def item_rows(folder, id_field, loaded_at):
    rows = []
    for path in sorted((RAW_DIR / folder).glob("repo=*/*.json")):
        content = read_json(path)
        for item in content[folder]:
            rows.append(
                {
                    "repo": content["repo"],
                    id_field: item[id_field],
                    "batch_id": batch_id_for(path),
                    "extracted_at": content["extracted_at"],
                    "loaded_at": loaded_at,
                    "payload": json.dumps(item),
                }
            )
    return rows


def batch_keys(table_name, rows):
    if table_name == "repo_snapshots":
        return sorted({f"{row['snapshot_date']}|{row['repo']}" for row in rows})
    return sorted({row["batch_id"] for row in rows})


def delete_existing(client, table_id, table_name, keys):
    if table_name == "repo_snapshots":
        key_expression = "CONCAT(CAST(snapshot_date AS STRING), '|', repo)"
    else:
        key_expression = "batch_id"

    query = f"DELETE FROM `{table_id}` WHERE {key_expression} IN UNNEST(@keys)"
    job_config = bigquery.QueryJobConfig(
        query_parameters=[bigquery.ArrayQueryParameter("keys", "STRING", keys)]
    )
    job = client.query(query, job_config=job_config)
    job.result()
    return job.num_dml_affected_rows or 0


def load_table(client, project_id, table_name, rows):
    if not rows:
        logger.info("%s: no rows to load", table_name)
        return

    table_id = f"{project_id}.{DATASET}.{table_name}"
    keys = batch_keys(table_name, rows)
    deleted = delete_existing(client, table_id, table_name, keys)

    job_config = bigquery.LoadJobConfig(
        write_disposition=bigquery.WriteDisposition.WRITE_APPEND
    )
    job = client.load_table_from_json(rows, table_id, job_config=job_config)
    job.result()
    logger.info(
        "%s: replaced %s old rows with %s rows (%s batches)",
        table_name,
        deleted,
        len(rows),
        len(keys),
    )


def main():
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s"
    )
    project_id = os.getenv("GCP_PROJECT_ID")
    client = bigquery.Client(project=project_id)
    loaded_at = datetime.now(UTC).isoformat()

    sources = {
        "repo_snapshots": snapshot_rows(loaded_at),
        "repositories": repository_rows(loaded_at),
        "commits": item_rows("commits", "sha", loaded_at),
        "issues": item_rows("issues", "number", loaded_at),
        "pull_requests": item_rows("pulls", "number", loaded_at),
    }

    for table_name, rows in sources.items():
        load_table(client, project_id, table_name, rows)


if __name__ == "__main__":
    main()