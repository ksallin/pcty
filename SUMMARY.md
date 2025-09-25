
## Bugs Fixed

1. **legislative_rag.py**: Regex parsing of `'PASS/FAIL'` and `':'` mismatched with `constants.py`, causing a constant `False` result.
2. **legislative_rag.py**: Dataset uses `'state'`, not `'slate'`.
3. **legislative_rag.py**: Changed `ascending=True` to `ascending=False` so sorting is from largest to smallest.
4. **legislative_rag.py**: Added `lawfulness_key` to detect both `'ETHICAL'` and `'LAWFULNESS'`. Updated logic from `or` → `and` so both criteria must pass.
5. **tfidf_searcher.py**: Similarity always returned `0` due to integer casting. Fixed by converting to `float`.
6. **legislative_rag.py**: Replaced `loc` with `iloc` since `loc` always returned index `0`.
7. **evaluation.py**: `self.df["actual_response"] == self.df["actual_response"]` always evaluated `True`. Corrected to use `self.df["expected_response"]` from `reference_dataset.csv`.
8. **evaluation.py**: Accuracy calculation mistakenly counted positives twice. Corrected one to negatives.
9. **mock_llm_agent.py**: Removed duplicate `import pickle`.

## Improvements

1. **evaluation.py**: Added a method to check the type of `df["user_background"]`, if it is string or dictionary.
2. **legislative_rag.py**: Fixed string concatenation in
   ```
   query = question + background_info.get("state", "")
   ```
which produced no spacing and confused tokenization. Updated to a more robust approach.
3. **evaluation.py**: Replaced python ```self.df["user_background"].ne({}) ``` with python ```self.df["user_background"].apply(lambda x: len(x) > 0)``` to ensure background data actually exists.
4. **legislative_rag.py**: Added logging and try/except handling to improve error resilience and prevent crashes.
5. **tfidf_searcher.py**: Added logging and input validation to handle null values or invalid inputs gracefully.
6. **mock_llm_agent.py**: Added logging, try/except, and input validation to address silent failures.
7. **tfidf_searcher.py**: Normalized 'questions' before processing for more consistent results.

## Metrics

Output of application includes accuracy, precision, recall, and F1 score at *k*th retrieval.
Results:

```json
{
  "accuracy - overall": 0.7857,
  "accuracy - positive": 0.6667,
  "accuracy - negative": 1.0000,
  "accuracy - background awareness": 1.0000,

  "precision_at_3 - overall": 0.1905,
  "precision_at_3 - positive": 0.2963,
  "precision_at_3 - negative": 0.0000,

  "recall_at_3 - overall": 0.5714,
  "recall_at_3 - positive": 0.8889,
  "recall_at_3 - negative": 0.0000,

  "f1_at_3 - overall": 0.2857,
  "f1_at_3 - positive": 0.4444,
  "f1_at_3 - negative": 0.0000
}
```
## Insights

- **Accuracy (positive):** 66.7% → Final success rate
- **Recall@3 (positive):** 88.9% → The system finds the correct articles most of the time
- **Precision@3 (positive):** 29.6% → However, many of the top 3 results are irrelevant

In short, the system successfully retrieves the right articles about 89% of the time, but only ~30% of the top-ranked results are truly relevant, indicating a high level of noise.

## Proposal

1. **Automatic vendor switching (PCTY <--> PCTY2)**
   - Add health checks and routing to switch vendors if one fails.
   - Goal: prevent outages and improve reliability.

2. **Run models in parallel for comparison**
   - Send the same query to multiple retrievers (TF-IDF, PCTY, PCTY2, etc.).
   - Collect and compare results side by side.
   - Goal: measure which model works best.

3. **Improve retrieval model (beyond TF-IDF)**
   - TF-IDF has poor precision (too much noise).
   - Use embeddings (e.g., BERT/SBERT) or LLM-based re-ranking.
   - Goal: enhance the performance.

