from create_bigquery_tables import TABLES


def test_each_table_is_partitioned_on_a_column_in_its_schema():
    for name, spec in TABLES.items():
        column_names = [field.name for field in spec["schema"]]
        assert spec["partition_field"] in column_names, name


def test_each_table_has_repo_and_loaded_at():
    for name, spec in TABLES.items():
        column_names = [field.name for field in spec["schema"]]
        assert "repo" in column_names, name
        assert "loaded_at" in column_names, name