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
    if verbose: print('>>>ALL_RES:', list_result)
    list_result = list(zip(*list_result)) #group the vars/args of all results 
    if verbose: print('>>>GROUPED_RES:', list_result)
    # Remove 'health-ontology.' prefix from each result
    cleaned_result = []
    for arg in list_result:
        cleaned_arg = []
        for item in arg:
            item = str(item)
            if item.startswith("health-ontology."):
                cleaned_arg.append(item.split("health-ontology.", 1)[1])
            else:
                cleaned_arg.append(item)
        if len(arg)>1: cleaned_result.append(', '.join(cleaned_arg)) 
        else: cleaned_result.append(cleaned_arg[0])
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


def recipe_by_health(ontology_graph, recipe: str, condition: str): #! in report: doesn't take foodswap info into account -> future 
    query = f"""
        SELECT DISTINCT ?ingredient ?cause 
        WHERE {{
            :{condition} :mightBeCausedBy ?cause .
            :{recipe} :hasFood ?ingredient .
            ?ingredient :hasNutrient ?cause 
        }}
    """
    return generic_query(
        ontology_graph,
        query,
        f"{condition} might be caused by {{1}} which is contained in {{0}} which is an ingredient in {recipe}",
        f"{condition} is not caused by eating {recipe}",
        empty_answer=False,
    )


def not_sport_and_sport(ontology_graph, not_sport: str, sport: str):
    query = f"""
        SELECT ?condition
        WHERE {{
            ?condition :mightBeCausedBy :{sport} .
            ?condition :canNotPerform :{not_sport} .
        }}
    """
    return generic_query(
        ontology_graph,
        query,
        f"a(n) {{0}} can be caused by {sport} and prevents doing any {not_sport}",
        f"{sport} does not cause a condition that prevents doing any {not_sport}",
        empty_answer=False,
    )


def sport_promotes_over_sport(ontology_graph, sport: str, sport2: str):
    query = f"""
        SELECT ?benefit
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
        f"{{0}} is promoted by {sport} but not by {sport2}",
        f"{sport} does not promote any benefits that {sport2} doesn't",
        empty_answer=False,
    )


def recipe_fuels_sport(ontology_graph, recipe: str, sport: str):
    query = f"""
        SELECT ?nutrient ?ingredient
        WHERE {{
            # ?sport rdf:type/rdfs:subClassOf* :Sport .
            :{sport} :decreasesNutrient ?nutrient .
            :{recipe} :hasFood ?ingredient .
            ?ingredient :hasNutrient ?nutrient .
        }}
    """
    return generic_query(
        ontology_graph,
        query,
        f"{sport} decreases {{0}} and {recipe} contains {{1}} which contains {{0}}",
        f"{recipe} does not contain any nutrients that {sport} decreases",
        empty_answer=False,
    )


def allergy_eat_recipe(ontology_graph, allergy: str, recipe: str): #TODO: FIX THIS 
    # Food and containedBy value ramen 
    # (Food and not (hasAllergen some (triggersAllergy  value egg_allergy))) or hasSwap some (not(hasAllergen some (triggersAllergy value egg_allergy)))
    query = f"""
        SELECT ?ingredient ?allergen ?swap
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
            :{recipe} :hasFood ?ingredient .
            ?ingredient :hasAllergen ?allergen .
            ?allergen :triggersAllergy :{allergy} .
            ?ingredient :hasSwap ?swap .
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
        f"all ingredients in {recipe} do not contain a food that triggers an allergy to {allergy.split('_')[0]}, if the following swaps are peformed: {{0}} --> {{2}}",
        f"{recipe} triggers an allergy to {allergy.split('_')[0]} and it does not have a swap",
        empty_answer=False,
    )


def recipe_help_symptoms(ontology_graph, recipe: str, symptoms: list[str]): #TODO: FIX THIS 
    # hasSymptom value dizzy and hasSymptom value fever is a subset of shouldEat some (containedBy value tagine)
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
        SELECT ?condition 
        WHERE {{
            ?condition :hasSymptom :{' ; :hasSymptom :'.join(symptoms)} .
            ?condition :canPerform :{sport} .
        }}
    """
    return generic_query(
        ontology_graph,
        query,
        f"{{0}} has these symptoms, but still lets you perform {sport}",
        f"there is no condition with {', '.join(symptoms)} as symptopms that still lets you do {sport}",
        empty_answer=False,
    )


# Dictionary of all query functions
query_functions = {
    "Recipe_by_Health": recipe_by_health,
    "not_Sport_and_Sport": not_sport_and_sport,
    "Sport_promotes_over_Sport": sport_promotes_over_sport,
    "Recipe_fuels_Sport": recipe_fuels_sport,
    "Allergy_eat_Recipe": allergy_eat_recipe,
    "Recipe_help_Symptom": recipe_help_symptoms,
    "Sport_with_Symptom": sport_with_symptoms,
}
