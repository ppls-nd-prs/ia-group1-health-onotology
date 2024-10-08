import os
from collections import namedtuple

from dotenv import load_dotenv

IsTruth = namedtuple(
    "IsTruth", ["is_true", "explanation"]
)  # is_truth: Boolean | None, explanation: String


load_dotenv()
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
