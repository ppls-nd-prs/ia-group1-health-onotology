from re import L

from src.utils import IsTruth


def run_query(ontology_graph, query: str, verbose=False) -> list:
    full_query = f"""
            PREFIX : <http://www.semanticweb.org/uu/ia/group1/health/ontology#>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX owl: <http://www.w3.org/2002/07/owl#>
                {query}
            """

    result = ontology_graph.query_owlready(full_query)
    list_result = list(result)
    if verbose:
        print(">>>ALL_RES:", list_result)
    list_result = list(zip(*list_result))  # group the vars/args of all results
    if verbose:
        print(">>>GROUPED_RES:", list_result)
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
        cleaned_result.append(cleaned_arg)

    return cleaned_result


def check_query(
    result: list,
    positive_explanation: str,
    negative_explanation: str,
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
    expected_answer: str | None = None,
    verbose=False,
):
    result = run_query(ontology_graph, query, verbose)
    if verbose:
        print(">>>", result)
    if len(result) > 0:
        formatted_positive_explanation = positive_explanation.format(*result).replace(
            "_", " "
        )
        formatted_negative_explanation = negative_explanation.format(*result).replace(
            "_", " "
        )
    else:
        formatted_positive_explanation = positive_explanation.replace("_", " ")
        formatted_negative_explanation = negative_explanation.replace("_", " ")
    return check_query(
        result,
        formatted_positive_explanation,
        formatted_negative_explanation,
        expected_answer,
    )


def recipe_by_health(
    ontology_graph, recipe: str, condition: str, verbose=False
):  #! in report: doesn't take foodswap info into account -> future
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
        f"{recipe} does not contain anything that could cause {condition}",
        verbose=verbose,
    )


def not_sport_and_sport(ontology_graph, not_sport: str, sport: str, verbose=False):
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
        verbose=verbose,
    )


def sport_promotes_over_sport(ontology_graph, sport: str, sport2: str, verbose=False):
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
        verbose=verbose,
    )


def recipe_fuels_sport(ontology_graph, recipe: str, sport: str, verbose=False):
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
        verbose=verbose,
    )


def allergy_eat_recipe(ontology_graph, allergy: str, recipe: str, verbose=False):
    # Food and containedBy value ramen
    # (Food and not (hasAllergen some (triggersAllergy  value egg_allergy))) or hasSwap some (not(hasAllergen some (triggersAllergy value egg_allergy)))
    query = f"""
        SELECT ?ingredient ?swap
        WHERE {{
        {{ 
            ?ingredient rdf:type/rdfs:subClassOf* :Food .
            FILTER NOT EXISTS {{
                ?ingredient :hasAllergen ?allergen .
                ?allergen :triggersAllergy :{allergy} .
            }}
        }} 
        UNION 
        {{ 
            ?ingredient rdf:type/rdfs:subClassOf* :Food .
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

    query2 = f"""
        SELECT ?ingredient
        WHERE {{
            :{recipe} :hasFood ?ingredient .
        }}
    """

    swap_food = run_query(ontology_graph, query, verbose)

    recipe_food = run_query(ontology_graph, query2, verbose)

    safe_ingredients = set(swap_food[0])
    recipe_ingredients = set(recipe_food[0])

    if recipe_ingredients.issubset(safe_ingredients):
        swaps = [
            f"{ingredient} --> {swap}"
            for ingredient, swap in zip(swap_food[0], swap_food[1])
            if swap != "None"
        ]
        allergy_type = allergy.split("_")[0]
        positive_explanation = (
            f"All ingredients in {recipe} are safe for {allergy_type} allergy"
        )
        if swaps:
            positive_explanation += f", with the following swaps: {', '.join(swaps)}"
        return IsTruth(True, positive_explanation)

    unsafe_ingredients = recipe_ingredients - safe_ingredients
    allergy_type = allergy.split("_")[0]
    negative_explanation = f"{recipe} contains {', '.join(unsafe_ingredients)} which triggers a {allergy_type} allergy and has no safe substitutes"
    return IsTruth(False, negative_explanation)


def recipe_help_symptoms(
    ontology_graph, recipe: str, symptoms: list[str], verbose=False
):  # TODO: FIX THIS
    # hasSymptom value dizzy and hasSymptom value fever is a subset of shouldEat some (containedBy value tagine)
    query = f"""
        SELECT ?condition
        WHERE {{
            ?condition :hasSymptom :{' ; :hasSymptom :'.join(symptoms)} .
        }}
    """

    query2 = f"""
        SELECT ?condition ?food
        WHERE {{
            ?condition :shouldEat ?food .
            ?food :containedBy :{recipe} .
        }}
    """

    condition_list = run_query(ontology_graph, query, verbose)

    conditions = set(condition_list[0])

    conditions_and_food = run_query(ontology_graph, query2, verbose)
    recipe_for_conditions = set(conditions_and_food[0])
    recipe_food = set(conditions_and_food[1])

    if conditions.issubset(recipe_for_conditions):
        return IsTruth(
            True,
            f"{', '.join(conditions)} {'have' if len(conditions) > 1 else 'has'} symptom(s) {', '.join(symptoms)}. {recipe} helps with this because it has {' ,'.join(recipe_food)}",
        )

    not_helped_symptoms = conditions - recipe_for_conditions
    negative_explanation = f"{', '.join(not_helped_symptoms)} {'have' if len(not_helped_symptoms) > 1 else 'has'} symptom(s) {', '.join(symptoms)} which are not helped by {recipe}"
    return IsTruth(False, negative_explanation)


def sport_with_symptoms(ontology_graph, sport: str, symptoms: list[str], verbose=False):
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
        verbose=verbose,
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
