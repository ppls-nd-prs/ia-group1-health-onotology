from owlready2 import *

from src.queries import *
from src.utils import IsTruth

import re


class OntologyCheck:
    symptoms = '(?:an |a )?(\w*(?: \w*)?)(?: and (?:an |a )?(\w*))?'
    sport = '(?:play |perform )?(.*)'
    sporting = '(?:playing |performing )?(.*)'

    Recipe_by_Health = (re.compile('Does eating (.*) cause (.*)\?'), 'Recipe_by_Health')
    Sport_and_not_Sport = (re.compile(f'Can not being able to {sport} be caused by {sporting}\?'), 'Sport_and_not_Sport')
    Sport_promotes_over_Sport = (re.compile(f'Does {sporting} provide any health benefit that is not provided by {sporting}\?'), ) 
    Recipe_fuels_Sport = (re.compile(f'Does (.*) provide the required nutrients for {sporting}\?'), 'Sport_promotes_over_Sport')
    Allergy_eat_Recipe = (re.compile(f'Can someone with (?:an|a) (.*) eat (.*)\?'), 'Allergy_eat_Recipe')
    Recipe_help_Symptom = (re.compile(f'Does eating (.*) help against {symptoms}\?'), 'Recipe_help_Symptom')
    Sport_with_Symptom = (re.compile(f'Is it possible that you are able to {sport} with {symptoms}\?'), 'Sport_with_Symptom') 

    patterns = [Recipe_by_Health, Sport_and_not_Sport, Sport_promotes_over_Sport, Recipe_fuels_Sport, Allergy_eat_Recipe, Recipe_help_Symptom, Sport_with_Symptom]

    def __init__(self):
        my_world = World()
        my_world.get_ontology("health-ontology.rdf").load()
        sync_reasoner(
            my_world, infer_property_values=True
        )  # reasoner is started and synchronized here)  # reasoner is started and synchronized here
        self.graph = my_world.as_rdflib_graph()

    def ontology_check_truth(self, user_input: str):
        for pattern in self.patterns: 
            if p := pattern[0].match(user_input):
                arg1 = '_'.join(p.groups()[0].split(' '))
                if len(p.groups()) > 2:
                    arg2 = ['_'.join(a.split(' ')) for a in p.groups()[1:]]
                else: 
                    arg2 = '_'.join(p.groups()[1].split(' '))
                if self.check_if_in_ontology(pattern[1], arg1, arg2):
                    return query_functions[pattern[1]](self.graph, arg1, arg2)
        raise ValueError(f"Unknown query: {user_input}")

  
    def check_if_in_ontology(self, pattern, arg1, arg2):
        classes = re.findall(r'\b[A-Z][a-z]*\b', pattern)
        if arg1 in classes[0]:
        
        if type(arg2) == list: 
            for arg in arg2: 
                if arg in classes[1]
        else: 
            if arg2 in classes[1]


