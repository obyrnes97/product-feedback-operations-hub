# Product Feedback Operations Hub — Learning Log

This document records what I build, learn, test, and debug during the 14-day project.

## Day 1 — Define the MVP

**What I built**

- Defined the problem, target user, inputs and AI outputs.
- Created the feedback taxonomy and classification categories.
- Defined the MVP scope and non-goals.

**What I learned**

- Define the problem and user before building.
- A taxonomy gives the AI consistent categories for classification.
- Scope and non-goals keep an MVP focused.

**Data flow**\
Customer feedback → AI classification → structured output

## Day 2 — Set Up the App

**What I built**

- Created the GitHub repository.
- Created `app.py` and the first Streamlit page.
- Created `requirements.txt` with Streamlit and pandas.
- Created a virtual environment and ran the app locally.
- Committed and pushed the code to GitHub.

**What I learned**

- `app.py` contains the main application code.
- `requirements.txt` lists the packages the app needs.
- A virtual environment keeps this project's Python packages isolated.
- Git tracks changes; GitHub stores the remote repository.
- Add → commit → push is the basic Git workflow.

**Data flow**\
Python code → Streamlit → local web app

## Day 3 — Create Sample Data

**What I built**

- Created `sample_feedback.csv` with 30 customer feedback examples.
- Included clear and ambiguous feedback to later test the AI classification against our taxonomy.
- Committed and pushed the file to GitHub.

**What I learned**

- A CSV stores tabular data using rows and columns.
- Good test data should include both simple and ambiguous cases.

**Data flow**\
Customer feedback → CSV → application

## Day 4 — Build CSV Upload

**What I built**

- Added a CSV upload button to the Streamlit app.
- Used pandas to read the uploaded CSV.
- Displayed all 30 rows as a table in the app.

**What I learned**

- `st.file_uploader()` lets the user upload a file.
- `pd.read_csv()` turns the CSV into a pandas DataFrame.
- A DataFrame is a table of data that Python can work with.

**Data flow**\
CSV → Streamlit upload → pandas → DataFrame → displayed in app

## Day 7 — Prompt Design and Evaluation

**What I built**

- Created a versioned classification prompt system and saved Prompt V1 in `prompts/feedback_classification_v1.md`.
- Created a reusable evaluation harness using 10 fixed feedback comments with expected classifications.
- Added prompt-version selection and evaluation results to Streamlit.
- Created Prompt V2 only after V1 testing showed specific failure patterns.

**V1 results**

- `feedback_type`: 8/10 (80%).
- `product_theme`: 6/10 (60%).
- `severity`: 8/8 scored cases (100%).

The main problems were:

- The model sometimes chose `product_theme` based on the feature or business area mentioned rather than the nature of the problem.
- The model sometimes inferred a usability or navigation problem from ambiguous feedback without enough evidence.

**Changes made in V2**

- Added guidance to classify product theme according to the nature of the primary problem.
- Added stronger guidance requiring evidence before assigning a specific feedback type or product theme.
- Preserved V1 instead of overwriting it so the versions could be compared.
- Did not change the severity rules.

**V2 results**

- `feedback_type`: 9/10 (90%).
- `product_theme`: 8/10 (80%).
- `severity`: 7/8 scored cases (87.5%).

**What I learned**

- Evaluate prompt quality using repeatable test cases rather than judging a few outputs informally.
- Target prompt changes at observed failure patterns rather than rewriting everything.
- LLM outputs can vary between runs. A small evaluation set and a single run provide useful signals, but do not prove production-level accuracy.
- Versioning prompts makes it possible to compare changes and avoid losing earlier versions.
- Keep expected answers separate from the information sent to the model so they do not influence its answers and contaminate the evaluation.
- Structured JSON makes model output easier for Python to validate and compare.

**Remaining limitations**

- V2 still misclassified some test cases.
- The 10-case evaluation set is small.
- Ambiguous severity is difficult to evaluate because the taxonomy only allows High, Medium, or Low. Two cases deliberately had no expected severity and were excluded from severity scoring.
- Before production use, I would expand the evaluation dataset and run repeated evaluations.
