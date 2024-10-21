import anthropic

from src.utils import ANTHROPIC_API_KEY, IsTruth

_client = None


def llm_check_truth(user_input: str) -> IsTruth:

    # Initialize the Anthropic client
    global _client
    if _client is None:
        _client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    # Construct the prompt for Claude
    prompt = f"""
    You are a truth-checking AI. Your task is to determine if the following statement is true or false, and provide a brief explanation for your decision.

    Statement: "{user_input}"

    Please respond in the following format:
    Is True: [Yes/No]
    Explanation: [Your explanation here]
    """

    # Send the message to Claude and get the response
    response = _client.messages.create(
        model="claude-3-haiku-20240307",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1024,
    )

    # Parse the response
    lines = response.content[0].text.strip().split("\n")
    is_true = lines[0].split(":")[1].strip().lower() == "yes"
    explanation = lines[1].split(":")[1].strip()

    return IsTruth(is_true=is_true, explanation=explanation)
