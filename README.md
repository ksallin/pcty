pcty_crab
-------------------------------

[![Package Version](https://img.shields.io/badge/Version-0.1.0-005A9C.svg?style=flat&logo=github)](https://github.com/Paylocity/dst-pcty_crab)
[![Python](https://img.shields.io/badge/Made%20with-Python-005A9C.svg?style=flat&logo=python)](https://www.python.org/)
[![Python Requirements](https://img.shields.io/badge/Python-3.7+-005A9C.svg?style=flat&logo)](https://www.python.org/downloads/release/python-360/)
[![Black](https://img.shields.io/badge/Code%20Style-black-000000.svg)](https://github.com/psf/black)

Challenge: RAG Application with Bugs

View the current release and new features and fixes via the [CHANGELOG.md](https://github.com/Paylocity/dst-pcty_crab/blob/main/CHANGELOG.md).

### How to Use the pcty_crab Repo:
Please add instructions on how to use the package (Feel free to delete if not applicable).

Project Structure
---------------
```
    $
    |-- pcty_crab
    |   |-- data_preperation
    |   |-- modelling
    |   |-- monitoring
    |   |-- plotting
    |   |-- utils
    |   |   |-- constants.py
    |   |   |-- dag_constants.py
    |   |   |-- file_paths.py
    |   |   |-- helpers.py
    |   |-- manifest.yml
    |   |-- VERSION
    |-- aws_infrastructure
    |   |-- AWSDeployment.Dockerfile
    |   |-- helpers.py
    |   |-- stack_deploy.sh
    |-- deployment
    |   |-- run_scripts
    |   |   |-- data_prep.py
    |   |   |-- model_pipeline.py
    |-- tests
    |   |-- pcty_crab
    |   |   |-- test_pcty_crab.py
    |   |-- conftest.py
    |-- .bumpversion.cfg
    |-- .editorconfig
    |-- .env.example
    |-- .gitchangelog.rc
    |-- .gitignore
    |-- .pre-commit-config.yaml
    |-- API.Dockerfile
    |-- catalog-info.yaml
    |-- CHANGELOG.md
    |-- Dockerfile
    |-- Makefile
    |-- MANIFEST.in
    |-- pyproject.toml
    |-- README.md
    |-- requirement.json
    |-- setup.py
    ```

Developer Setup
---------------
Want to help contribute to the package? Great, let's get started.
1. Refer to the [Data Science Code Contribution Guidelines wiki](https://paylocity.atlassian.net/wiki/x/ggCjC).
2. Ensure that the working branch is up-to-date with the main branch.
3. Ensure make is installed on your machine.
4. In the terminal run commands to create the _pcty_crab_ conda environment and install dependencies:
   ```
   conda activate base
   make env
   conda activate pcty_crab
   make env-init
   ```

Automated code quality tools
----------------------------
Automated code quality tools created to help improving the code quality
and finding potential bugs. Consulting these tools before submitting the
merge request can significantly save the time of the developer and
reviewers.

The workflow might looks like this:
1. Develop your awesome feature
2. Run `make lint` to get a list of potential issues including the best effort
   in auto-fixing the issues
3. Fix other issues if you find them important, or ignore them. Consult
   <https://beta.ruff.rs/docs/configuration/#error-suppression> for the
   ways to ignore the errors using the standard ruff mechanism. In this way
   ruff will skip those suppressed errors in upcoming checks.
4. Submit merge request
```
Package Release Steps
---------------------
We fixed / added some stuff. Woohoo! Now what? To release the package [follow these instructions](https://paylocity.atlassian.net/wiki/x/ywCjC).





This repo was built with love using the <a href='https://github.com/Paylocity/dst-pcty_spider/'>pcty_spider</a> repo (version 4.4.1).
