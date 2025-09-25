import pickle
import re
from dataclasses import dataclass, field
import logging
import pandas as pd
from pcty_crab.base.mock_llm_agent import LLMClient
from pcty_crab.base.tfidf_searcher import TfidfSearcher
from pcty_crab.utils.constants import (
    FALLBACK_RESPONSE,
    PROMPTS,
    SEARCHER_PICKLE_PATH, VENDOR,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class LegislativeRAG:
    """RAG executor for legislative documents using a prebuilt TF-IDF searcher."""
    #Improve: Add try/catch and logging
    searcher: TfidfSearcher = field(init=False)
    vendor: str = field(init=True,default=VENDOR)

    def __post_init__(self):
        """Load the pickled TF-IDF searcher into self.searcher."""
        try:
            with open(SEARCHER_PICKLE_PATH, "rb") as f:
                self.searcher = pickle.load(f)
            logger.info(f"Successfully loaded searcher from {SEARCHER_PICKLE_PATH}")
        except FileNotFoundError:
            logger.error(f"Searcher file not found: {SEARCHER_PICKLE_PATH}")
            raise RuntimeError(f"Required searcher file not found: {SEARCHER_PICKLE_PATH}")
        except pickle.PickleError as e:
            logger.error(f"Failed to load searcher pickle: {e}")
            raise RuntimeError(f"Corrupted searcher file: {SEARCHER_PICKLE_PATH}")
        except Exception as e:
            logger.error(f"Unexpected error loading searcher: {e}")
            raise RuntimeError(f"Failed to initialize searcher: {e}")

    def search(self, query: str) -> pd.DataFrame:
        """Run similarity search over all articles and return a sorted DataFrame."""
        try:

            if not query or not isinstance(query, str):
                logger.warning(f"Invalid query: {query}")
                return pd.DataFrame(columns=["doc_index", "article_title", "similarity"])
            if self.searcher is None:
                logger.error("Searcher not initialized")
                raise RuntimeError("Search system not available")
            results_df = self.searcher.search_all(query)
            if results_df.empty:
                logger.warning(f"No search results for query: {query[:50]}...")
                return results_df
            results_df.sort_values(
                # Bug: for descending sort to get the biggest similarity on the top, so ascending=True -> False
                "similarity", ascending=False, kind="mergesort", inplace=True
            )
            logger.info(f"Search returned {len(results_df)} results for query")
            return results_df
        except Exception as e:
            logger.error(f"Search failed for query '{query[:50]}...': {e}")
            return pd.DataFrame(columns=["doc_index", "article_title", "similarity"])


    def prompt_filtering(self, query: str) -> dict:
        """Call LLM to evaluate prompt filtering criteria with error handling."""
        try:
            if not query or not isinstance(query, str):
                logger.warning(f"Invalid query for filtering: {query}")
                return {}
            llm_client = LLMClient(vendor=self.vendor)
            # Get response and parse criteria results
            response = llm_client.ask_llm(
                system_prompt=PROMPTS.get(self.vendor, ""),
                user_prompt=query
            )
            if not response:
                logger.warning("Empty response from LLM client")
                return {}
            # Parse response with regex
            #Bug: fix to match constants.py format
            pattern = r"(\w+):\s*(PASS|FAIL)"
            matches = re.findall(pattern, response)
            if not matches:
                logger.warning(f"No criteria matches found in LLM response: {response[:100]}...")
                return {}
            results = dict(matches)
            logger.info(f"Prompt filtering results: {results}")
            return results
        except Exception as e:
            logger.error(f"Prompt filtering failed for query '{query[:50]}...': {e}")
            return {}

    def run_qa(self, question: str, background_info: dict = None) -> str:
        """Run search and prompt filtering with comprehensive error handling."""
        try:
            if not question or not isinstance(question, str):
                logger.error(f"Invalid question: {question}")
                return "Invalid question provided"
            if background_info is None:
                background_info = {}
            elif not isinstance(background_info, dict):
                logger.warning(f"Invalid background_info type: {type(background_info)}")
                background_info = {}
            try:
                #Bug: fix change "slate" -> "state"
                #improve: use secure concate method
                state = background_info.get("state", "")
                if state and isinstance(state, str):
                    query = f"{question} {state}".strip()
                else:
                    query = question
                logger.info(f"Built search query: {query[:100]}...")
            except Exception as e:
                logger.warning(f"Query construction failed: {e}, using question only")
                query = question

            results_df = self.search(query)

            if results_df.empty:
                logger.warning("No search results found")
                return "No relevant information found"
            try:
                #Bug: change from loc to iloc, always return the first row
                top_result = results_df.iloc[0]["article_title"]
                logger.info(f"Top search result: {top_result}")
            except (IndexError, KeyError) as e:
                logger.error(f"Failed to get top result: {e}")
                return "Search results unavailable"
            pf_scores = self.prompt_filtering(question)
            if not pf_scores:
                logger.warning("Prompt filtering failed - rejecting by default")
                return FALLBACK_RESPONSE
            try:
                #Bug: we need to check ETHICAL and LAWFULNESS both, rather than only one status
                lawfulness_key = "ETHICAL" if self.vendor == "PCTY2" else "LAWFULNESS"
                lawfulness_pass = pf_scores.get(lawfulness_key) == "PASS"
                scope_pass = pf_scores.get("SCOPE") == "PASS"
                if lawfulness_pass and scope_pass:
                    logger.info("Question passed all filtering criteria")
                    return top_result
                else:
                    logger.info(
                        f"Question failed filtering: {lawfulness_key}={pf_scores.get(lawfulness_key)}, SCOPE={pf_scores.get('SCOPE')}")
                    return FALLBACK_RESPONSE
            except Exception as e:
                logger.error(f"Filtering logic failed: {e}")
                return FALLBACK_RESPONSE
        except Exception as e:
            logger.error(f"Unexpected error in run_qa: {e}")
            return "System temporarily unavailable"


if __name__ == "__main__":

    rag = LegislativeRAG()

    result = rag.run_qa("What is the minimum wage?", {"state": "california"})

    print(result)

    result = rag.run_qa("How do I pay employees less if they are older than a certain age?", {})

    print(result)
