from src.query_catalog import QUERY_DIR, load_catalog


def test_every_catalog_entry_has_a_select_query():
    catalog = load_catalog()
    assert len(catalog) >= 10
    for definition in catalog.values():
        path = QUERY_DIR / definition.sql_file
        assert path.exists(), definition.query_id
        sql = definition.sql.strip().upper()
        assert sql.startswith("SELECT")
        assert not any(word in sql for word in [" UPDATE ", " DELETE ", " INSERT ", " DROP "])


def test_query_ids_are_stable_and_unique():
    catalog = load_catalog()
    assert len(catalog) == len(set(catalog))
    assert "department_activity" in catalog
    assert catalog["department_activity"].join_type == "LEFT JOIN"

