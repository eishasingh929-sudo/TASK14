from uniguru.service.query_classifier import QueryType, classify_query


def test_query_classifier_identifies_web_lookup() -> None:
    assert classify_query("What is the latest weather today?") == QueryType.WEB_LOOKUP


def test_query_classifier_identifies_concept_query() -> None:
    assert classify_query("What is ahimsa?") == QueryType.CONCEPT_QUERY


def test_query_classifier_identifies_explanation_query() -> None:
    assert classify_query("Explain superposition in simple terms") == QueryType.EXPLANATION_QUERY


def test_query_classifier_defaults_to_knowledge_query() -> None:
    assert classify_query("Jain ethics principles") == QueryType.KNOWLEDGE_QUERY
