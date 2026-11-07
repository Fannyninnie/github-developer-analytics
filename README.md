# GitHub Developer Activity Analytics

End-to-end data pipeline that ingests public GitHub activity,
loads it into BigQuery, models it with dbt, and orchestrates it with Airflow.

## Status
In development (Day 1 of 35)

## Planned stack
Python, GitHub REST API, BigQuery, dbt, Airflow, Docker, Looker Studio

## Architecture
Diagram coming on Day 5.

## Roadmap
- [ ] API ingestion (incremental)
- [ ] BigQuery raw layer
- [ ] dbt staging and marts
- [ ] Data quality tests and CI
- [ ] Airflow orchestration
- [ ] Dashboard