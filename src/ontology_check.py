from owlready2 import *
from rdflib import URIRef
from rdflib.namespace import RDF

from src.queries import *
from src.utils import IsTruth

import re


class OntologyCheck:
    prefix = "http://www.semanticweb.org/uu/ia/group1/health/ontology#"

    symptoms = '(?:an |a )?(\w*(?: \w*)?)(?: and (?:an |a )?(\w*(?: \w*)?))?' #!in report: 1-2 symptoms 
    sport = '(?:play |perform |do )?(.*)'
    sporting = '(?:playing |performing |do )?(.*)'

    Recipe_by_Health = (re.compile('Does eating (.*) cause (.*)\?'), 'Recipe_by_Health')
    not_Sport_and_Sport = (re.compile(f'Can not being able to {sport} be caused by {sporting}\?'), 'not_Sport_and_Sport')
    Sport_promotes_over_Sport = (re.compile(f'Does {sporting} provide any health benefit that is not provided by {sporting}\?'), 'Sport_promotes_over_Sport') 
    Recipe_fuels_Sport = (re.compile(f'Does (.*) provide the required nutrients for {sporting}\?'), 'Recipe_fuels_Sport')
    Allergy_eat_Recipe = (re.compile(f'Can someone with (?:an|a) (.*) eat (.*)\?'), 'Allergy_eat_Recipe')
    Recipe_help_Symptom = (re.compile(f'Does eating (.*) help against {symptoms}\?'), 'Recipe_help_Symptom')
    Sport_with_Symptom = (re.compile(f'Is it possible that you are able to {sport} with {symptoms}\?'), 'Sport_with_Symptom') 

    patterns = [Recipe_by_Health, not_Sport_and_Sport, Sport_promotes_over_Sport, Recipe_fuels_Sport, Allergy_eat_Recipe, Recipe_help_Symptom, Sport_with_Symptom]

    def __init__(self):
        self.my_world = World()
        self.my_world.get_ontology("health-ontology.rdf").load()
        sync_reasoner(
            self.my_world, infer_property_values=True
        )  # reasoner is started and synchronized here)  # reasoner is started and synchronized here
        self.graph = self.my_world.as_rdflib_graph()

    def ontology_check_truth(self, user_input: str, verbose = False):
        for pattern in self.patterns: 
            if p := pattern[0].match(user_input):
                arg1 = '_'.join(p.groups()[0].split(' '))
                if len(p.groups()) > 2:
                    arg2 = ['_'.join(a.split(' ')) for a in p.groups()[1:] if a is not None] #remove optional groups that were not filled 
                else: 
                    arg2 = '_'.join(p.groups()[1].split(' '))
                if self.check_if_in_ontology(pattern[1], arg1, arg2, verbose):
                    if verbose: print('>>>QUERY:', pattern[1], arg1, arg2)
                    return query_functions[pattern[1]](self.graph, arg1, arg2, verbose)
        print('Unknown query, please try again.')
        return 
  
    def check_if_in_ontology(self, pattern, arg1, arg2, verbose = False):
        classes = re.findall(r'[A-Z][a-z]*', pattern)
        # check if in onottlogy at all 
        for a, c in zip([arg1, arg2], classes):
            if verbose: print('>>>CHECKING:', a, c )
            a_ont = URIRef(self.prefix + a)
            if not (a_ont, RDF.type, None) in self.graph:
                print(f"There is no knowledge available about {a}. To perform any reasoning about this concept, the ontolgy should be updated.")
                return False
            # TODO fix this 
            # c_ont = URIRef(self.prefix + c) 
            # if not (a_ont, RDF.type, c_ont) in self.graph:
            #     print(f"Unable to proceed because {a} is not an instance of {c}.")
            #     return False
            
        return True 