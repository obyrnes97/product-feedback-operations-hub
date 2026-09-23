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
