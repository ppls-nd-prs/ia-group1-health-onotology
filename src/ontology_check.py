from owlready2 import *

from src.utils import IsTruth


class OntologyCheck:
    def __init__(self):
        my_world = World()
        my_world.get_ontology("test_ont.rdf").load()
        sync_reasoner(
            my_world, infer_property_values=True
        )  # reasoner is started and synchronized here)  # reasoner is started and synchronized here
        self.graph = my_world.as_rdflib_graph()

    def ontology_check_truth(self, user_input: str) -> IsTruth:

        query = """
                PREFIX : <http://www.semanticweb.org/jip/ontologies/2024/9/untitled-ontology-23#>
                PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                PREFIX owl: <http://www.w3.org/2002/07/owl#>
                    SELECT ?x
                    WHERE {
                        :ramen :contains ?x .
                    }
                """

        # Sport and decreasesNutrient some (containedBy value ramen)

        resultsList = self.graph.query(query)

        print(list(resultsList))

    def parse_natural_language_to_ontology_query(self, user_input: str) -> dict:
        pass

    def create_explanation_from_ontology(self):
        pass
