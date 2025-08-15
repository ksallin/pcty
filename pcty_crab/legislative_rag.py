from dataclasses import dataclass, field
import pickle
import pandas as pd

from pcty_crab.utils.constants import SEARCHER_PICKLE_PATH
from pcty_crab.preparation.tfidf_searcher import TfidfSearcher


@dataclass
class LegislativeRAG:
    """RAG executor for legislative documents using a prebuilt TF-IDF searcher."""
    searcher: TfidfSearcher = field(init=False)

    def __post_init__(self) -> None:
        """Load the pickled TF-IDF searcher into self.searcher."""
        with open(SEARCHER_PICKLE_PATH, "rb") as f:
            self.searcher = pickle.load(f)

    def search(self, query: str) -> pd.DataFrame:
        """Run similarity search over all articles and return a sorted DataFrame."""
        results_df = self.searcher.search_all(query)

        results_df.sort_values("similarity", ascending=False, kind="mergesort", inplace=True)
        return results_df

    def run_qa(self, question: str, background_info: dict = None) -> dict:
        """Run search and prompt filtering"""

        result = {}

        # Create search query
        query = question + background_info["state"] if background_info else question

        # Get similarity scores between query and articles
        results_df = self.search(query)

        # Get the top article
        result["article_title"] = results_df.iloc[0]["article_title"]

        return result

if __name__ == "__main__":

    rag = LegislativeRAG()

    result = rag.run_qa(
        "what is the minimum wage?",
        {"state": "california"}
    )

    print(result)

