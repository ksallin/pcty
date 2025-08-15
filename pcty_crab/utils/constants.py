from pathlib import Path

# Paths
PACKAGE_DIR = Path(__file__).parent.parent
RESOURCES_DIR = PACKAGE_DIR / "resources"
ARTICLES_PICKLE_PATH = RESOURCES_DIR / "articles.pkl"
SEARCHER_PICKLE_PATH = RESOURCES_DIR / "searcher.pkl"
