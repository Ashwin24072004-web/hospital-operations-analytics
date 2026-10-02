from src.retrieval import rank_glossary, rank_queries


def test_department_question_ranks_department_activity_first():
    ranked = rank_queries("Which department has the most appointments?")
    assert ranked[0].definition.query_id == "department_activity"


def test_doctor_workload_question_retrieves_doctor_summary():
    query_ids = [item.definition.query_id for item in rank_queries("Compare doctor workloads")]
    assert "doctor_summary" in query_ids[:3]


def test_revenue_definition_retrieves_metric_glossary():
    sections = rank_glossary("What does collected revenue mean?")
    assert sections[0].title == "Metrics"

