from typing import List, Dict, Optional, Tuple
import re
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
import pickle

from pcty_crab.utils.constants import (
    ARTICLES_PICKLE_PATH,
    SEARCHER_PICKLE_PATH,
)


class TfidfSearcher:
    """
    TF-IDF–based searcher that indexes articles and ranks them against a query.

    Parameters
    ----------
    ngram_range : tuple(int, int), default=(1, 2)
        Range of n-grams for tokenization.
    max_df : float, default=0.95
        Ignore terms with document frequency higher than this proportion.
    min_df : int, default=1
        Ignore terms with document frequency lower than this absolute count.
    max_features : int or None, default=None
        Limit on vocabulary size.
    stop_words : str, list, or None, default="english"
        Stop words to remove from the documents.
    title_weight : int, default=3
        Number of times to repeat the normalized title text for weighting.
    """

    def __init__(
        self,
        ngram_range: Tuple[int, int] = (1, 2),
        max_df: float = 0.95,
        min_df: int = 1,
        max_features: Optional[int] = None,
        stop_words: Optional[str] = "english",
        title_weight: int = 3,
    ) -> None:
        """Initialize vectorizer configuration and internal state."""
        self.vectorizer = TfidfVectorizer(
            ngram_range=ngram_range,
            max_df=max_df,
            min_df=min_df,
            max_features=max_features,
            stop_words=stop_words,
            lowercase=False,  # we normalize explicitly
        )
        self.title_weight = title_weight
        self._ws_re = re.compile(r"\s+")
        self.docs: List[str] = []
        self.meta: List[Dict] = []
        self.X = None

    def _normalize(self, text: str) -> str:
        """Lowercase, trim, and collapse whitespace for stable indexing."""
        if not text:
            return ""
        text = text.lower().strip()
        return self._ws_re.sub(" ", text)

    def _make_doc(self, title: str, content: str) -> str:
        """Build a weighted document string by boosting title and appending content."""
        t = self._normalize(title)
        c = self._normalize(content or "")
        boosted_title = (" " + t) * self.title_weight
        return (t + boosted_title + " " + c).strip()

    def fit(self, articles: List[Dict[str, str]]) -> "TfidfSearcher":
        """Create the TF-IDF index from a list of article dictionaries."""
        self.docs = [self._make_doc(a["article_title"], a.get("article_content", "")) for a in articles]
        self.meta = [
            {"idx": i, "article_title": a["article_title"], "article_content": a.get("article_content", "")}
            for i, a in enumerate(articles)
        ]
        self.X = self.vectorizer.fit_transform(self.docs)
        return self

    def search_all(self, question: str) -> pd.DataFrame:
        """Return similarity scores for all indexed articles"""
        if not self.docs or self.X is None:
            raise RuntimeError("Call fit() before search_all().")

        q_vec = self.vectorizer.transform([self._normalize(question)])
        scores = linear_kernel(q_vec, self.X).ravel()

        df = pd.DataFrame({
            "doc_index": [m["idx"] for m in self.meta],
            "article_title": [m["article_title"] for m in self.meta],
            "similarity": scores.astype(float),
        })
        return df

if __name__ == "__main__":

    # Create searcher

    with open(ARTICLES_PICKLE_PATH, "rb") as f:
        data = pickle.load(f)

    searcher = TfidfSearcher(title_weight=4)
    searcher.fit(data)

    with open(SEARCHER_PICKLE_PATH, "wb") as f:
        pickle.dump(searcher, f)
