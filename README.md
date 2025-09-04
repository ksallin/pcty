pcty_crab
-------------------------------
Challenge: RAG Application with Bugs

# Background
You are a data scientist developing a chatbot that helps HR practitioners find relevant legislative information
from a collection of articles. As of now, there is only a search and prompt filtering component.
When a user submits a question (e.g., "What is the 401K limit for 2025?"), the bot returns the most relevant article
title from a knowledge base, as long as the question is within scope.

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
To prevent application misuse, the submitted question must then pass two criteria evaluated by an LLM:
* LAWFULNESS - questions does not seek information to help break the law or perpetuate discriminatory practices
* SCOPE - question related to government, HR, or company policies

Note: for the purpose of this exercise, we are not actually evaluating the criteria with a LLM. Instead, we have dummy
function to return a pre-drafted response based on the question. Therefore, any changes to the LLM prompt will not
impact the response returned.

# Developer Setup
This application requires the following packages installed in your environment to run:
* pandas==2.3.2
* scikit-learn==1.7.1
* python-dotenv==1.1.1


```
This repo was built with love using the <a href='https://github.com/Paylocity/dst-pcty_spider/'>pcty_spider</a>
repo (version 4.4.1).
