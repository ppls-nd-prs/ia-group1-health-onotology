import owlready2
from owlready2 import *

from src.utils import IsTruth


def ontology_check_truth(user_input: str) -> IsTruth:
    onto = get_ontology("path/to/your/ontology.owl").load()
    query = parse_natural_language_to_ontology_query(user_input)
    results = query_ontology(query, onto)
    return results


def parse_natural_language_to_ontology_query(user_input: str) -> dict:
    pass


def create_explanation_from_ontology():
    pass


def query_ontology(query: dict, onto: Ontology):
    results = onto.search(**query)
    return results
