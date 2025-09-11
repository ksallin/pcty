"""Top-level package for pcty_crab."""

from pathlib import Path


__version__ = (Path(__file__).parent / "VERSION").read_text().strip()

__author__ = """Paylocity Data Science Team"""
__email__ = "pctydatascience@paylocity.com"

__all__ = ["__version__"]
