from owlready2 import *

from src.queries import *
from src.utils import IsTruth
from fuzzywuzzy import fuzz


class OntologyCheck:
    def __init__(self):
        my_world = World()
        my_world.get_ontology("health-ontology.rdf").load()
        sync_reasoner(
            my_world, infer_property_values=True
        )  # reasoner is started and synchronized here)  # reasoner is started and synchronized here
        self.graph = my_world.as_rdflib_graph()

    def get_query_from_user_input(self, user_input: str) -> query_answer_tuple:
        predefined_questions = {
            "Does eating pasta bolognese cause high cholesterol?": "high_cholesterol_by_pasta",
            "Can not being able to walk be caused by playing field hockey?": "fieldhockey_and_not_walk",
            "Does walking provide any health benefit that is not provided by weightlifting?": "walking_promotes_over_weightlifting",
            "Does ramen provide the required nutrients for weightlifting?": "weight_lifting_decreases_nutrient",
            "Can someone with an egg allergy eat ramen?": "ramen_has_egg_swap",
            "Does eating tagine help against dizziness and a fever?": "tagine_help_dizzy_fever",
            "Is it possible that you are able to play soccer with dizziness and a fever?": "soccer_with_dizzy_fever",
        }

        best_match = self.get_best_match_fuzzywuzzy(user_input, predefined_questions)

        if best_match:
            return queries[predefined_questions[best_match]]
        else:
            raise ValueError(f"No similar query found for: {user_input}")

    def get_best_match_fuzzywuzzy(self, user_input, predefined_questions, threshold=70):
        best_ratio = 0
        best_match = None
        for question in predefined_questions:
            ratio = fuzz.token_sort_ratio(user_input.lower(), question.lower())
            if ratio > best_ratio and ratio >= threshold:
                best_ratio = ratio
                best_match = question
        return best_match

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
