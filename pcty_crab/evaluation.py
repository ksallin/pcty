from ast import literal_eval
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional, Union

import pandas as pd

from pcty_crab.base.legislative_rag import LegislativeRAG
from pcty_crab.base.tfidf_searcher import TfidfSearcher
from pcty_crab.utils.constants import REFERENCE_DATASET_PATH


@dataclass
class PerformanceEvaluator:
    """
    Evaluate the performance of a LegislativeRAG model against a labeled QA dataset.

    This class:
      - Loads a dataset from CSV containing questions, user background info,
        expected response type, and expected responses.
      - Runs the LegislativeRAG model on each question with its background info.
      - Compares actual vs expected responses.
      - Computes simple accuracy metrics (overall, positive, negative).
    """
    dataset_path: Union[str, Path]

    def __post_init__(self):
        self.dataset_path = Path(self.dataset_path)
        self.df = pd.read_csv(self.dataset_path)

        required = {
            "question",
            "user_background",
            "expected_response_type",
            "expected_response",
        }
        missing = required - set(self.df.columns)
        if missing:
            raise ValueError(
                f"Dataset missing required columns: {sorted(missing)}"
            )

        self.df["user_background"] = self.df["user_background"].apply(
            lambda x: literal_eval(x)
        )

        self.rag = LegislativeRAG()

    def evaluate(self) -> Dict[str, Optional[float]]:
        """
        Run evaluation by:
          - Passing each question & background through LegislativeRAG.
          - Comparing predicted responses with expected responses.
          - Returning accuracy metrics (overall, positive, negative).
        """
        # Run the model on each row and collect actual responses
        actual_responses = []
        for _, row in self.df.iterrows():
            resp = self.rag.run_qa(
                question=row["question"],
                background_info=row["user_background"],
            )
            actual_responses.append(resp)

        # Store predictions and correctness in dataframe
        self.df["actual_response"] = actual_responses
        self.df["is_correct"] = (
            self.df["expected_response"] == self.df["actual_response"]
        )

        # Helper function to calculate accuracy safely
        def _acc(mask: pd.Series) -> Optional[float]:
            denom = int(mask.sum())
            if denom == 0:
                return None  # Avoid divide-by-zero
            return float(self.df.loc[mask, "is_correct"].mean())

        # Compute accuracy metrics
        metrics = {
            "accuracy - overall": _acc(pd.Series(True, index=self.df.index)),
            "accuracy - positive": _acc(
                self.df["expected_response_type"].eq("positive")
            ),
            "accuracy - negative": _acc(
                self.df["expected_response_type"].eq("negative")
            ),
        }


if __name__ == "__main__":

    evaluator = PerformanceEvaluator(dataset_path=REFERENCE_DATASET_PATH)
    results = evaluator.evaluate()
    print(results)
