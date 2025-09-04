import pickle

from pcty_crab.utils.constants import LLM_REFERENCE_PATH


class LLMClient:
    """
    A mock LLM client that returns a pre-determined response based on the query
    """
    def __init__(self, vendor):
        # Initialize vendor
        self.vendor = vendor
        # Load reference information
        with open(LLM_REFERENCE_PATH, "rb") as f:
            self.reference = pickle.load(f)

    def ask_llm(self, system_prompt: str, user_prompt: str) -> str:
        """
        Returns pre-determined response based on user prompt
        """

        # Generate a response
        response = self.reference.get(
            user_prompt,
            "Sorry, I don’t have an answer to that question right now.",
        )

        if self.vendor == "PCTY":
            return response
        else:
            return response.replace("LAWFULNESS", "ETHICAL")
