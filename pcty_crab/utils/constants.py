from pathlib import Path


# Paths
PACKAGE_DIR = Path(__file__).parent.parent
RESOURCES_DIR = PACKAGE_DIR / "resources"
ARTICLES_PICKLE_PATH = RESOURCES_DIR / "articles.pkl"
SEARCHER_PICKLE_PATH = RESOURCES_DIR / "searcher.pkl"
REFERENCE_DATASET_PATH = RESOURCES_DIR / "reference_dataset.csv"
LLM_REFERENCE_PATH = RESOURCES_DIR / "qa.pkl"

# Prompts
PROMPTS = {
    "PCTY": """
You serve as an intelligent filter for incoming client questions, ensuring only valid inquiries passes through.

** Client Filtering Criteria **
LAWFULNESS: questions does not seek information to help break the law or perpetuate discriminatory practices
SCOPE: question related to government, HR, or company policies

** Output Format **
criteria: PASS or FAIL, short reason
        """,
    "PCTY2": """
You serve as an intelligent filter for incoming client questions, ensuring only valid inquiries passes through.

** Client Filtering Criteria **
ETHICAL: questions perpetuate unethical practices
SCOPE: question related to government, HR, or company policies

** Output Format **
criteria: PASS or FAIL, short reason
        """,
}

FALLBACK_RESPONSE = "Rejected question"
