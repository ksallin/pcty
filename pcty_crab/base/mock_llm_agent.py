# import pickle

from pcty_crab.utils.constants import LLM_REFERENCE_PATH
from dataclasses import dataclass, field
import pickle
from typing import Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
#improve: try/catch, invalid input and fix silent process
@dataclass
class LLMClient:
    """
    A mock LLM client that returns a pre-determined response based on the query.
    """
    vendor: str
    reference: Dict[str, str] = field(init=False, repr=False)

    def __post_init__(self):
        # Load reference information once instance is created
        try:
            with open(LLM_REFERENCE_PATH, "rb") as f:
                self.reference = pickle.load(f)
            logger.info(f"Loaded {len(self.reference)} mock LLM responses")
        except FileNotFoundError:
            logger.error(f"Mock LLM reference file not found: {LLM_REFERENCE_PATH}")
            self.reference = {}
        except Exception as e:
            logger.error(f"Failed to load mock LLM reference: {e}")
            self.reference = {}

    def ask_llm(self, system_prompt: str, user_prompt: str) -> str:
        """
        Returns pre-determined response based on user prompt with proper fallback.
        """
        try:
            response = self.reference.get(user_prompt)
            if response is None:
                logger.warning(f"No mock response found for question: '{user_prompt[:50]}...'")
                return "No mock rseponse file"
            if self.vendor == "PCTY":
                return response
            return response.replace("LAWFULNESS", "ETHICAL")
        except Exception as e:
            logger.error(f"Mock LLM failed for question '{user_prompt[:50]}...': {e}")
            error_response = "LAWFULNESS: FAIL, System error\nSCOPE: FAIL, System error"
            if self.vendor == "PCTY":
                return error_response
            else:
                return error_response.replace("LAWFULNESS", "ETHICAL")
