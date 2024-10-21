from src.llm_check import llm_check_truth
from src.ontology_check import OntologyCheck
from src.utils import IsTruth


def sense_user_input() -> str:
    input("Press Enter to continue...")
    user_input = input("Enter your input: ")
    return user_input


def choose_appropriate_response(is_true_llm: IsTruth, is_true_ontology: IsTruth) -> str:
    trustworthy_verdict = "true" if is_true_ontology.is_true else "false"
    less_trustworthy_verdict = "true" if is_true_llm.is_true else "false"
    final_verdict = (
        trustworthy_verdict
        if is_true_ontology.is_true is not None
        else less_trustworthy_verdict
    )

    response = []
    if is_true_ontology.is_true is not None:
        response.append(
            f"A trustworthy source says this is {trustworthy_verdict} because {is_true_ontology.explanation}."
        )
    else:
        response.append("This cannot be verified through a trustworthy source.")

    response.append(
        f"A less trustworthy source says this is {less_trustworthy_verdict} because {is_true_llm.explanation}."
    )

    if is_true_ontology.is_true is None:
        response.append(
            f"Therefore, we can conclude that the statement may be {final_verdict}."
        )
    else:
        response.append(
            f"Therefore, we can conclude that the statement is {final_verdict}."
        )

    return "\n".join(response)


def main():
    user_input = sense_user_input()
    is_true_llm = llm_check_truth(user_input)
    is_true_ontology = ontology_check_truth(user_input)

    response = choose_appropriate_response(is_true_llm, is_true_ontology)
    print(response)


if __name__ == "__main__":
    ontology = OntologyCheck()
    is_true_ontology = ontology.ontology_check_truth("test")

    # main()
