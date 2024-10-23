from owlready2 import *

from src.queries import *
from src.utils import IsTruth


class OntologyCheck:
    def __init__(self):
        my_world = World()
        my_world.get_ontology("health-ontology.rdf").load()
        sync_reasoner(
            my_world, infer_property_values=True
        )  # reasoner is started and synchronized here)  # reasoner is started and synchronized here
        self.graph = my_world.as_rdflib_graph()

    def get_query_from_user_input(self, user_input: str) -> query_answer_tuple:
        match user_input:
            case "Does eating pasta bolognese cause high cholesterol?":
                return queries["high_cholesterol_by_pasta"]
            case "Can not being able to walk be caused by playing field hockey?":
                return queries["fieldhockey_and_not_walk"]
            case "Does walking provide any health benefit that is not provided by weightlifting?":
                return queries["walking_promotes_over_weightlifting"]
            case "Does ramen provide the required nutrients for weightlifting?":
                return queries["weight_lifting_decreases_nutrient"]
            case "Can someone with an egg allergy eat ramen?":
                return queries["ramen_has_egg_swap"]
            case "Does eating tagine help against dizziness and a fever?":
                return queries["tagine_help_dizzy_fever"]
            case "Is it possible that you are able to play soccer with dizziness and a fever?":
                return queries["soccer_with_dizzy_fever"]
            case _:
                raise ValueError(f"Unknown query: {user_input}")

    def ontology_check_truth(self, user_input: str) -> IsTruth:
        related_query = self.get_query_from_user_input(user_input)
        query = f"""
                PREFIX : <http://www.semanticweb.org/uu/ia/group1/health/ontology#>
                PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                PREFIX owl: <http://www.w3.org/2002/07/owl#>
                    {related_query.query}
                """

        results = self.graph.query_owlready(query)
        resultsList = list(results)[0]

        if related_query.any_answer:
            correct = len(resultsList) > 0
            return IsTruth(
                correct,
                related_query.explanation.format(*resultsList),
            )
        if related_query.expected_answer is None:
            return IsTruth(
                len(resultsList) == 0,
                related_query.explanation.format(*resultsList),
            )
        for result in resultsList:
            if related_query.expected_answer in str(result):
                return IsTruth(
                    True,
                    related_query.explanation.format(*resultsList),
                )
        return IsTruth(False, related_query.explanation.format(*resultsList))
