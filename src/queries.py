from re import L

from src.utils import IsTruth


def run_query(ontology_graph, query: str) -> list:
    full_query = f"""
            PREFIX : <http://www.semanticweb.org/uu/ia/group1/health/ontology#>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX owl: <http://www.w3.org/2002/07/owl#>
                {query}
            """
    result = ontology_graph.query_owlready(full_query)
    list_result = list(result)
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
):
    result = run_query(ontology_graph, query)
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


def recipe_by_health(ontology_graph, food: str, condition: str):
    query = f"""
        SELECT DISTINCT ?condition (:{food} AS ?food) ?cause 
        WHERE {{
            ?condition rdf:type/rdfs:subClassOf* :Health .
            ?condition :mightBeCausedBy ?cause .
            :{food} :contains ?cause .
        }}
    """
    return generic_query(
        ontology_graph,
        query,
        "{0} might be caused by {1} because it contains {2}",
        f"{condition} is not caused {food}",
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


def sport_promoted_by_food(ontology_graph, sport: str, food: str):
    query = f"""
        SELECT ?sport ?nutrient (:{food} AS ?food) ?ingredient
        WHERE {{
            ?sport rdf:type/rdfs:subClassOf* :Sport .
            ?sport :decreasesNutrient ?nutrient .
            :{food} :contains ?ingredient .
            ?ingredient :contains ?nutrient .
        }}
    """
    return generic_query(
        ontology_graph,
        query,
        "{0} decreases {1} but {2} contains {3}",
        f"{food} does not contain any nutrients that {sport} decreases",
        empty_answer=False,
        expected_answer=sport,
    )


def food_has_allergy_swap(ontology_graph, dish: str, allergy: str):
    # Food and containedBy value ramen 
    # (Food and not (hasAllergen some (triggersAllergy  value egg_allergy))) or hasSwap some (not(hasAllergen some (triggersAllergy value egg_allergy)))
    query = f"""
        SELECT ?ingredient ?allergen (:{allergy} AS ?egg)
            WHERE {{
                :{dish} :hasFood ?ingredient .
                :{allergy} :triggersAllergy ?allergen

                FILTER NOT EXISTS {{
                    ?ingredient :hasAllergen ?allergen .
                }}
                FILTER NOT EXISTS {{
                    ?ingredient :hasSwap ?swap .
                    ?swap :hasAllergen ?allergen
                }}
            }}
    """

    return generic_query(
        ontology_graph,
        query,
        f"all ingredients in {dish} do not contain {allergy} of have a swap",
        "{0} contains {1} but does not have a swap",
        empty_answer=True,
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
        f"you can perform {sport} with these symptoms {', '.join(symptoms)}",
        empty_answer=False,
    )


# Dictionary of all query functions
query_functions = {
    "Recipe_by_Health": recipe_by_health,
    "Sport_and_not_Sport": sport_and_not_sport,
    "Sport_promotes_over_Sport": sport_promotes_over_sport,
    "Recipe_fuels_Sport": sport_promoted_by_food,
    "Allergy_eat_Recipe": food_has_allergy_swap,
    "Recipe_help_Symptom": recipe_help_symptoms,
    "Sport_with_Symptom": sport_with_symptoms,
}
