from typing import NamedTuple

query_answer_tuple = NamedTuple(
    "query_answer_tuple",
    [
        ("query", str),
        ("expected_answer", str | None),
        ("any_answer", bool),
        ("explanation", str),
    ],
)

# expected_answer: "answer" for should contain, None for empty list

queries = {
    "high_cholesterol_by_pasta": query_answer_tuple(
        query="""
        SELECT DISTINCT ?condition (:pasta_bolognese AS ?food) ?cause 
        WHERE {
            ?condition rdf:type/rdfs:subClassOf* :Health .
            ?condition :mightBeCausedBy ?cause .
            :pasta_bolognese :contains ?cause .
        }
    """,
        expected_answer="high_cholesterol",
        any_answer=False,
        explanation="{0} might be caused by {1} because it contains {2}",
    ),
    "fieldhockey_and_not_walk": query_answer_tuple(
        query="""
        SELECT ?condition (:field_hockey AS ?sport) (:walking AS ?sport2)
        WHERE {
            ?condition :mightBeCausedBy :field_hockey .
            ?condition :canNotPerform :walking .
        }
    """,
        expected_answer=None,
        any_answer=True,
        explanation="{0} can be caused by {1} and prevents {2}",
    ),
    "weight_lifting_decreases_nutrient": query_answer_tuple(
        query="""
        SELECT ?sport ?nutrient (:ramen AS ?food) ?ingredient
        WHERE {
            ?sport rdf:type/rdfs:subClassOf* :Sport .
            ?sport :decreasesNutrient ?nutrient .
            :ramen :contains ?ingredient .
            ?ingredient :contains ?nutrient .
        }
    """,
        expected_answer="weight_lifting",
        any_answer=False,
        explanation="{0} decreases {1} but {2} contains {3}",
    ),
    "walking_promotes_over_weightlifting": query_answer_tuple(
        query="""
        SELECT ?benefit (:walking AS ?sport) (:weight_lifting AS ?sport2)
        WHERE {
            :walking :promotes ?benefit .
            FILTER NOT EXISTS {
                :weight_lifting :promotes ?benefit .
            }
        }
    """,
        expected_answer=None,
        any_answer=True,
        explanation="{0} promotes {1} but {2} does not",
    ),
    "ramen_has_egg_swap": query_answer_tuple(
        query="""
        SELECT ?ingredient (:egg AS ?egg) ?swap
            WHERE {
                :ramen :contains ?ingredient .
                ?ingredient :contains :egg .
                FILTER NOT EXISTS {
                    ?ingredient :hasSwap ?swap .
            }
            }
    """,
        expected_answer=None,
        any_answer=False,
        explanation="{0} contains {1} but does not have a swap",
    ),
    "tagine_help_dizzy_fever": query_answer_tuple(
        query="""
        SELECT ?condition
        WHERE {
            ?condition :hasSymptom :dizzy ;
                        :hasSymptom :fever .
            FILTER NOT EXISTS {
                ?condition :shouldEat ?food .
                ?food :containedBy :tagine .
            }
        }
    """,
        expected_answer=None,
        any_answer=False,
        explanation="Tagline satisfies all conditions with symptoms",
    ),
    "soccer_with_dizzy_fever": query_answer_tuple(
        query="""
        SELECT ?condition (:soccer AS ?sport)
        WHERE {
            ?condition :hasSymptom :dizzy ;
                        :hasSymptom :fever .
            ?condition :canPerform :soccer .
        }
        """,
        expected_answer=None,
        any_answer=True,
        explanation="{0} condition has these symptoms lets you perform soccer",
    ),
}
