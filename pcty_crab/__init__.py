"""Top-level package for pcty_crab."""
from pathlib import Path

from pcty_log import logger

logger.name = "pcty_crab"

__version__ = (Path(__file__).parent / "VERSION").read_text().strip()

__author__ = """Paylocity Data Science Team"""
__email__ = "pctydatascience@paylocity.com"

__all__ = ["__version__", "logger"]
