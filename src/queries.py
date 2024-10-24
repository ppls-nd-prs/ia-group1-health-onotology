from re import L

from src.utils import IsTruth


def run_query(ontology_graph, query: str, verbose = False) -> list:
    full_query = f"""
            PREFIX : <http://www.semanticweb.org/uu/ia/group1/health/ontology#>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX owl: <http://www.w3.org/2002/07/owl#>
                {query}
            """
    result = ontology_graph.query_owlready(full_query)
    list_result = list(result)
    if verbose: print('>>>', list_result)
    if len(list_result) > 0:
        list_result = list_result[0]
    # Remove 'health-ontology.' prefix from each result
    cleaned_result = []
    for item in list_result:
        item = str(item)
        if item.startswith("health-ontology."):
            cleaned_result.append(item.split("health-ontology.", 1)[1])
        else:
            cleaned_result.append(item)
    list_result = cleaned_result

    return list_result


def check_query(
    result: list,
    positive_explanation: str,
    negative_explanation: str,
    empty_answer: bool,
    expected_answer: str | None = None,
) -> IsTruth:
    if expected_answer:  # check if expected answer is in results
        for result in result:
            if expected_answer in str(result):
                return IsTruth(
                    True,
                    positive_explanation,
                )
        return IsTruth(
            False,
            negative_explanation,
        )
    if empty_answer:  # answer should be empty
        if len(result) > 0:
            return IsTruth(
                False,
                negative_explanation,
            )
        return IsTruth(
            True,
            positive_explanation,
        )
    if len(result) > 0:  # answer should not be empty
        return IsTruth(
            True,
            positive_explanation,
        )
    return IsTruth(
        False,
        negative_explanation,
    )


# expected_answer: "answer" for should contain, None for empty list


def generic_query(
    ontology_graph,
    query: str,
    positive_explanation: str,
    negative_explanation: str,
    empty_answer: bool,
    expected_answer: str | None = None,
    verbose = True  
):
    result = run_query(ontology_graph, query, verbose)
    if verbose: print('>>>', result)
    if len(result) > 0:
        formatted_positive_explanation = positive_explanation.format(*result)
        formatted_negative_explanation = negative_explanation.format(*result)
    else:
        formatted_positive_explanation = positive_explanation
        formatted_negative_explanation = negative_explanation
    return check_query(
        result,
        formatted_positive_explanation,
        formatted_negative_explanation,
        empty_answer,
        expected_answer,
    )


def recipe_by_health(ontology_graph, recipe: str, condition: str):
    query = f"""
        SELECT DISTINCT ?condition (:{recipe} AS ?food) ?cause 
        WHERE {{
            ?condition rdf:type/rdfs:subClassOf* :Health .
            ?condition :mightBeCausedBy ?cause .
            :{recipe} :contains ?cause .
        }}
    """
    return generic_query(
        ontology_graph,
        query,
        "{0} might be caused by {1} because it contains {2}",
        f"{condition} is not caused {recipe}",
        empty_answer=False,
        expected_answer=condition,
    )


def sport_and_not_sport(ontology_graph, sport: str, not_sport: str):
    query = f"""
        SELECT ?condition (:{sport} AS ?sport) (:{not_sport} AS ?sport2)
        WHERE {{
            ?condition :mightBeCausedBy :{sport} .
            ?condition :canNotPerform :{not_sport} .
        }}
    """
    return generic_query(
        ontology_graph,
        query,
        "{0} can be caused by {1} and prevents {2}",
        f"{sport} does not cause a condition that prevents {not_sport}",
        empty_answer=False,
    )


def sport_promotes_over_sport(ontology_graph, sport: str, sport2: str):
    query = f"""
        SELECT ?benefit (:{sport} AS ?sport) (:{sport2} AS ?sport2)
        WHERE {{
            :{sport} :promotes ?benefit .
            FILTER NOT EXISTS {{
                :{sport2} :promotes ?benefit .
            }}
        }}
    """
    return generic_query(
        ontology_graph,
        query,
        "{0} is promoted by {1} but not by {2}",
        f"{sport} does not promote any benefits that {sport2} doesn't",
        empty_answer=False,
    )


def recipe_fuels_sport(ontology_graph, recipe: str, sport: str):
    query = f"""
        SELECT ?sport ?nutrient (:{recipe} AS ?food) ?ingredient
        WHERE {{
            ?sport rdf:type/rdfs:subClassOf* :Sport .
            ?sport :decreasesNutrient ?nutrient .
            :{recipe} :contains ?ingredient .
            ?ingredient :contains ?nutrient .
        }}
    """
    return generic_query(
        ontology_graph,
        query,
        "{0} decreases {1} but {2} contains {3}",
        f"{recipe} does not contain any nutrients that {sport} decreases",
        empty_answer=False,
        expected_answer=sport,
    )


def allergy_eat_recipe(ontology_graph, allergy: str, recipe: str):
    # Food and containedBy value ramen 
    # (Food and not (hasAllergen some (triggersAllergy  value egg_allergy))) or hasSwap some (not(hasAllergen some (triggersAllergy value egg_allergy)))
    query = f"""
        SELECT ?ingredient ?allergen ?allergen_ingredient ?swap
        WHERE {{
        {{ 
            :{recipe} :hasFood ?ingredient .
            FILTER NOT EXISTS {{
                ?ingredient :hasAllergen ?allergen .
                ?allergen :triggersAllergy :{allergy} .
            }}
        }} 
        UNION 
        {{ 
            :{recipe} :hasFood ?allergen_ingredient .
            ?allergen_ingredient :hasAllergen ?allergen .
            ?allergen :triggersAllergy :{allergy} .
            ?allergen_ingredient :hasSwap ?swap .
            FILTER NOT EXISTS {{
                ?swap :hasAllergen ?swap_allergen .
                ?swap_allergen :triggersAllergy :{allergy} .
            }}
        }}
    }}
    """

    return generic_query(
        ontology_graph,
        query,
        f"all ingredients in {recipe} do not contain a food that triggers an allergy to {allergy.split('_')[0]}, or they have a swap",
        f"{recipe} triggers an allergy to {allergy.split('_')[0]} and it does not have a swap",
        empty_answer=False,
    )


def recipe_help_symptoms(ontology_graph, recipe: str, symptoms: list[str]):
    query = f"""
        SELECT ?condition
        WHERE {{
            ?condition :hasSymptom :{' ; :hasSymptom :'.join(symptoms)} .
            FILTER NOT EXISTS {{
                ?condition :shouldEat ?food .
                ?food :containedBy :{recipe} .
            }}
        }}
    """
    return generic_query(
        ontology_graph,
        query,
        f"{recipe} does helps with {' and '.join(symptoms)}",
        f"{{0}} has symptom {', '.join(symptoms)} which are not helped by {recipe}",
        empty_answer=True,
    )


def sport_with_symptoms(ontology_graph, sport: str, symptoms: list[str]):
    query = f"""
        SELECT ?condition (:{sport} AS ?sport)
        WHERE {{
            ?condition :hasSymptom :{' ; :hasSymptom :'.join(symptoms)} .
            ?condition :canPerform :{sport} .
        }}
    """
    return generic_query(
        ontology_graph,
        query,
        "{0} condition has these symptoms lets you perform {1}",
        f"you cannot perform {sport} with these symptoms {', '.join(symptoms)}",
        empty_answer=False,
    )


# Dictionary of all query functions
query_functions = {
    "Recipe_by_Health": recipe_by_health,
    "Sport_and_not_Sport": sport_and_not_sport,
    "Sport_promotes_over_Sport": sport_promotes_over_sport,
    "Recipe_fuels_Sport": recipe_fuels_sport,
    "Allergy_eat_Recipe": allergy_eat_recipe,
    "Recipe_help_Symptom": recipe_help_symptoms,
    "Sport_with_Symptom": sport_with_symptoms,
}
