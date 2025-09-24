from ast import literal_eval
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional, Union

import pandas as pd
from sklearn.metrics import precision_score

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
        # Improved: potentially if there are dicts in the dataset, it would raise error.
        def safe_eval(x):
            if isinstance(x, str):
                try:
                    return literal_eval(x)
                except Exception:
                    return x
            return x

        # Loading Evaluation Dataset
        self.dataset_path = Path(self.dataset_path)
        self.df = pd.read_csv(self.dataset_path)
              # self.df["user_background"] = self.df["user_background"].apply(
        #     lambda x: literal_eval(x)
        # )
        self.df["user_background"] = self.df["user_background"].apply(safe_eval)
        # defining Search object
        self.rag = LegislativeRAG(vendor="PCTY2")

    def evaluate(self) -> Dict[str, Optional[float]]:
        """
        Run evaluation by:
          - Passing each question & background through LegislativeRAG.
          - Comparing predicted responses with expected responses.
          - Returning accuracy metrics (overall, positive, negative).
        """
        # Run the model on each row and collect actual responses
        actual_responses = []
        precision_scores = []
        recall_scores = []
        f1_scores = []
        for _, row in self.df.iterrows():
            resp = self.rag.run_qa(
                question=row["question"],
                background_info=row["user_background"],
            )
            actual_responses.append(resp)

            # Calculate Precision@K for each query
            try:
                search_results = self.rag.search(row["question"])
                expected_answer = row["expected_response"]
                precision_at_k, recall_at_k, f1_at_k = self.calculate_precision_recall_f1_at_k(
                    search_results, expected_answer, k=3
                )
                precision_scores.append(precision_at_k)
                recall_scores.append(recall_at_k)
                f1_scores.append(f1_at_k)
            except Exception as e:
                print(f"Error calculating metrics for '{row['question'][:50]}...': {e}")
                precision_scores.append(0.0)
                recall_scores.append(0.0)
                f1_scores.append(0.0)

        # Store predictions and correctness in dataframe
        # Bug: always compare with actual response, need to compare to expected_responses
        self.df["actual_response"] = actual_responses
        self.df["is_correct"] = (
            # self.df["actual_response"] == self.df["actual_response"]
            self.df["actual_response"] == self.df["expected_response"]
        )
        self.df["precision_at_3"] = precision_scores
        self.df["recall_at_3"] = recall_scores
        self.df["f1_at_3"] = f1_scores
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
            #Bug: calculate positive twice
            "accuracy - negative": _acc(
                # self.df["expected_response_type"].eq("positive")
                self.df["expected_response_type"].eq("negative")
            ),
            "accuracy - background awareness": _acc(
                #Improve: check if user_background dict has any data
                # self.df["user_background"].ne({})
                self.df["user_background"].apply(lambda x: len(x) > 0)
            ),
            #improve: add precision/recall/f1
            "precision_at_3 - overall": self.df["precision_at_3"].mean(),
            "precision_at_3 - positive": self.df.loc[
                self.df["expected_response_type"].eq("positive"), "precision_at_3"
            ].mean(),
            "precision_at_3 - negative": self.df.loc[
                self.df["expected_response_type"].eq("negative"), "precision_at_3"
            ].mean(),
            "recall_at_3 - overall": self.df["recall_at_3"].mean(),
            "recall_at_3 - positive": self.df.loc[
                self.df["expected_response_type"].eq("positive"), "recall_at_3"
            ].mean(),
            "recall_at_3 - negative": self.df.loc[
                self.df["expected_response_type"].eq("negative"), "recall_at_3"
            ].mean(),
            "f1_at_3 - overall": self.df["f1_at_3"].mean(),
            "f1_at_3 - positive": self.df.loc[
                self.df["expected_response_type"].eq("positive"), "f1_at_3"
            ].mean(),
            "f1_at_3 - negative": self.df.loc[
                self.df["expected_response_type"].eq("negative"), "f1_at_3"
            ].mean(),
        }
        return metrics

    #improve: calculate precision/recall/f1
    def calculate_precision_recall_f1_at_k(self, search_results, expected_answer, k=3):
        if search_results.empty or k <= 0:
            return 0.0, 0.0, 0.0
        top_k = search_results.head(k)
        found_relevant = 0
        expected_lower = expected_answer.lower().strip()
        for _, row in top_k.iterrows():
            article_title = str(row["article_title"]).lower().strip()
            if article_title == expected_lower:
                found_relevant += 1
        total_relevant = 1
        precision = found_relevant / k
        recall = found_relevant / total_relevant
        if precision + recall == 0:
            f1 = 0.0
        else:
            f1 = 2 * (precision * recall) / (precision + recall)
        return precision, recall, f1

if __name__ == "__main__":

    evaluator = PerformanceEvaluator(dataset_path=REFERENCE_DATASET_PATH)
    results = evaluator.evaluate()
    print(results)
