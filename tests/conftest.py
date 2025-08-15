"""
Define testing artifacts that can be used across multiple tests here.
"""
import os

from pathlib import Path



# Solve issue in PyCharm when cwd is matching the parent of the script,
#   instead of the project dir
#   https://youtrack.jetbrains.com/issue/PY-50334
REPO_ROOT_DIR = Path(__file__).parents[1]
os.chdir(REPO_ROOT_DIR)
