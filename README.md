pcty_crab
-------------------------------
Challenge: RAG Application with Bugs

# Background
You are a data scientist in early stages of developing a chatbot that helps HR practitioners find relevant legislative
information from a collection of articles. As of now, there is only a search and prompt filtering component.
When a user submits a question (e.g., "What is the 401K limit for 2025?"), the bot returns the most relevant article
title from a knowledge base if the question passes all prompt filtering criteria.

# Your objective
Run the `evaluation.py` script to assess the application’s current performance. We suspect that silent bugs in the
repository are skewing the results. Identify and fix these bugs, rerun the evaluation and report the true performance
metrics.

## Email us back the following deliverables:
* Repo with code changes
* A text file with short summary of corrections made and the final metrics

## For discussion during our review session:
* What improvements would you make to enhance the performance of the existing application?
* What new features or enhancements would you propose to increase the value of the application?
* What are some additional metrics to track performance?

# Application overview
## Step-by-step process
* Application receives a question
* Search returns the most relevant article
* Prompt filtering passes or fails the question based on a set of criteria
  * If question passes all criteria - return the most relevant article
  * If question fails at least one criterion - return a fallback response

## Search
The system calculates a text similarity score between the user’s question and each article in the knowledge base
and returns the article with the highest similarity score. To improve search relevance, the user's location (state)
is injected into the search query when available

## Prompt filtering
To prevent application misuse, the submitted question must pass BOTH criteria by an LLM mocker:
* LAWFULNESS - questions does not seek information to help break the law or perpetuate discriminatory practices
* SCOPE - question related to government, HR, or company policies

Note: for the purpose of this exercise, we are not using an actual LLM to evaluate the criteria. Instead, we have dummy
function to return a pre-drafted response based on the question and vendor name. Therefore, any changes
to the LLM prompt will not impact the response returned.

# Developer Setup
This application requires the following packages installed in your environment to run:
* python>=3.9
* pandas==2.3.2
* scikit-learn==1.7.1

Project Structure
---------------
```
    |-- README.md                           <- Project overview (you are here)
    |-- pcty_crab                           <- Main application package
    |   |-- base                            <- Core application logic
    |   |   |-- legislative_rag.py          <- Implements pipeline: search + prompt filtering → generates responses
    |   |   |-- mock_llm_agent.py           <- Mock LLM agent for prompt filtering
    |   |   |-- tfidf_searcher.py           <- TF-IDF searcher: indexes articles and runs similarity search
    |   |
    |   |-- resources                       <- Prebuilt data and test artifacts
    |   |   |-- articles.pkl                <- Article contents
    |   |   |-- qa.pkl                      <- Q&A pairs (mock LLM responses)
    |   |   |-- reference_dataset.csv       <- Evaluation dataset of test questions
    |   |   |-- searcher.pkl                <- Pre-fitted TF-IDF search object (ready-to-use index)
    |   |
    |   |-- utils                           <- Shared constants and configs
    |   |   |-- constants.py                <- Paths and LLM prompt templates
    |   |
    |   |-- evaluation.py                   <- Start here: runs model evaluation on the reference dataset

```
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
3. **evaluation.py: Replaced python ```self.df["user_background"].ne({}) ``` with python ```self.df["user_background"].apply(lambda x: len(x) > 0)``` to ensure background data actually exists.
4. legislative_rag.py: Added logging and try/except handling to improve error resilience and prevent crashes.
5. tfidf_searcher.py: Added logging and input validation to handle null values or invalid inputs gracefully.
6. mock_llm_agent.py: Added logging, try/except, and input validation to address silent failures.
7. tfidf_searcher.py: Normalized 'questions' before processing for more consistent results.

## Metrics

Evaluation includes precision, recall, and F1 score at *k*th retrieval.
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

