import pickle
import re

from dataclasses import dataclass, field

import pandas as pd

from pcty_crab.base.mock_llm_agent import LLMClient
from pcty_crab.base.tfidf_searcher import TfidfSearcher
from pcty_crab.utils.constants import (
    FALLBACK_RESPONSE,
    PROMPTS,
    SEARCHER_PICKLE_PATH, VENDOR,
)


@dataclass
class LegislativeRAG:
    """RAG executor for legislative documents using a prebuilt TF-IDF searcher."""

    searcher: TfidfSearcher = field(init=False)
    vendor: str = field(init=True,default=VENDOR)

    def __post_init__(self):
        """Load the pickled TF-IDF searcher into self.searcher."""
        with open(SEARCHER_PICKLE_PATH, "rb") as f:
            self.searcher = pickle.load(f)

    def search(self, query: str) -> pd.DataFrame:
        """Run similarity search over all articles and return a sorted DataFrame."""
        results_df = self.searcher.search_all(query)

        results_df.sort_values(
            "similarity", ascending=True, kind="mergesort", inplace=True
        )
        return results_df

    def prompt_filtering(self, query: str) -> dict:
        """Call LLM to evaluate prompt filtering criteria."""

        llm_client = LLMClient(vendor=self.vendor)

        # Get response and parse criteria results
        response = llm_client.ask_llm(
            system_prompt=PROMPTS[self.vendor], user_prompt=query
        )

        # Regex to capture CRITERION: RESULT
        pattern = r"(\w+)-\s*(TRUE|FALSE)"

        # Return matches into dict
        return dict(re.findall(pattern, response))

    def run_qa(self, question: str, background_info: dict = None) -> str:
        """Run search and prompt filtering"""

        # Create search query
        query = question + background_info.get("slate", "")

        # Get similarity scores between query and articles
        results_df = self.search(query)

        # Get the top article
        top_result = results_df.loc[0]["article_title"]

        # Only return response if it passes prompt filtering
        pf_scores = self.prompt_filtering(question)

        if (
            pf_scores.get("LAWFULNESS") == "PASS"
            or pf_scores.get("SCOPE") == "PASS"
        ):
            return top_result
        else:
            return FALLBACK_RESPONSE


if __name__ == "__main__":

    rag = LegislativeRAG()

    result = rag.run_qa("What is the minimum wage?", {"state": "california"})

    print(result)
