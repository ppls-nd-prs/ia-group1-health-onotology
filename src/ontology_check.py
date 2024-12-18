import re

from owlready2 import *
from rdflib import URIRef
from rdflib.namespace import RDF

from src.queries import *
from src.utils import IsTruth


class OntologyCheck:
    prefix = "http://www.semanticweb.org/uu/ia/group1/health/ontology#"

    symptoms = "(?:an |a )?(\w*(?: \w*)?)(?: and (?:an |a )?(\w*(?: \w*)?))?"  #!in report: 1-2 symptoms
    sport = "(?:play |perform |do )?(.*)"
    sporting = "(?:playing |performing |doing )?(.*)"

    Recipe_by_Health = (re.compile("Does eating (.*) cause (.*)\?"), "Recipe_by_Health")
    not_Sport_and_Sport = (
        re.compile(f"Can not being able to {sport} be caused by {sporting}\?"),
        "not_Sport_and_Sport",
    )
    Sport_promotes_over_Sport = (
        re.compile(
            f"Does {sporting} provide any health benefit that is not provided by {sporting}\?"
        ),
        "Sport_promotes_over_Sport",
    )
    Recipe_fuels_Sport = (
        re.compile(f"Does (.*) provide the required nutrients for {sporting}\?"),
        "Recipe_fuels_Sport",
    )
    Allergy_eat_Recipe = (
        re.compile(f"Can someone with (?:an|a) (.*) eat (.*)\?"),
        "Allergy_eat_Recipe",
    )
    Recipe_help_Symptom = (
        re.compile(f"Does eating (.*) help against {symptoms}\?"),
        "Recipe_help_Symptom",
    )
    Sport_with_Symptom = (
        re.compile(f"Is it possible that you are able to {sport} with {symptoms}\?"),
        "Sport_with_Symptom",
    )

    patterns = [
        Recipe_by_Health,
        not_Sport_and_Sport,
        Sport_promotes_over_Sport,
        Recipe_fuels_Sport,
        Allergy_eat_Recipe,
        Recipe_help_Symptom,
        Sport_with_Symptom,
    ]

    def __init__(self):
        my_world = World()
        self.health_ontology = my_world.get_ontology("health-ontology.rdf").load()
        sync_reasoner(
            my_world, infer_property_values=True
        )  # reasoner is started and synchronized here

        self.graph = my_world.as_rdflib_graph()

    def ontology_check_truth(self, user_input: str, verbose=False):
        for pattern in self.patterns:
            if p := pattern[0].match(user_input):
                arg1 = "_".join(p.groups()[0].split(" "))
                if len(p.groups()) > 2:
                    arg2 = [
                        "_".join(a.split(" ")) for a in p.groups()[1:] if a is not None
                    ]  # remove optional groups that were not filled
                else:
                    arg2 = "_".join(p.groups()[1].split(" "))
                if self.check_if_in_ontology(pattern[1], arg1, arg2, verbose):
                    if verbose:
                        print(">>>QUERY:", pattern[1], arg1, arg2)
                    return query_functions[pattern[1]](self.graph, arg1, arg2, verbose)

        return IsTruth(None, "Unknown query, please try again.")

    def check_if_in_ontology(self, pattern, arg1, arg2, verbose=False):
        def check_instance(instance, class_name):
            instance_check = self.health_ontology.search(
                is_a=self.health_ontology[class_name], iri=f"*{instance}"
            )
            if len(instance_check) == 0:
                if verbose:
                    print(
                        f"There is no knowledge available about {class_name} {instance}. "
                        "To perform any reasoning about this concept, the ontology should be updated."
                    )
                return False
            return True

        classes = re.findall(r"[A-Z][a-z]*", pattern)
        for potential_instance, class_name in zip([arg1, arg2], classes):
            if verbose:
                print(">>>CHECKING:", potential_instance, class_name)
            if type(potential_instance) == list:
                for elem in potential_instance:
                    if not check_instance(elem, class_name):
                        return False
            else:
                if not check_instance(potential_instance, class_name):
                    return False

        return True
