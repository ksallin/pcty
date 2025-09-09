import pickle

from pcty_crab.utils.constants import LLM_REFERENCE_PATH


from dataclasses import dataclass, field
import pickle
from typing import Dict


@dataclass
class LLMClient:
    """
    A mock LLM client that returns a pre-determined response based on the query.
    """
    vendor: str
    reference: Dict[str, str] = field(init=False, repr=False)

    def __post_init__(self):
        # Load reference information once instance is created
        with open(LLM_REFERENCE_PATH, "rb") as f:
            self.reference = pickle.load(f)

    def ask_llm(self, system_prompt: str, user_prompt: str) -> str:
        """
        Returns pre-determined response based on user prompt.
        """
        response = self.reference.get(
            user_prompt,
            "Sorry, I don’t have an answer to that question right now.",
        )

        if self.vendor == "PCTY":
            return response
        return response.replace("LAWFULNESS", "ETHICAL")
