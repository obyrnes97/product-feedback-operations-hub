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

## Day 5 — Validate CSV Input

**What I built**

- Added input validation in `app.py` before displaying uploaded feedback.
- Checked for the six required columns, empty files, blank feedback text, and duplicate feedback IDs.
- Added understandable error messages, including affected feedback IDs where helpful.

**What I learned**

- Input validation happens before processing so malformed data produces understandable errors instead of breaking the application.
- pandas can identify missing values, blank text, and duplicate IDs.
- Rejecting invalid input makes problems visible instead of silently removing or changing records.

**Testing**

- Manually tested the CSV validation during guided testing.

**Data flow**\
CSV upload → pandas DataFrame → validation → error message or table preview

**Commit**

- `fd32749` — Add CSV input validation.

## Day 6 — Connect to the OpenAI API

**What I built**

- Added a button in `app.py` to classify one fixed feedback comment using OpenAI.
- Added the feedback taxonomy to `README.md` and the `openai` and `python-dotenv` packages to `requirements.txt`.
- Loaded the API key from local environment configuration and displayed the model response as JSON.
- Requested four fields at this stage: `feedback_type`, `product_theme`, `severity`, and a short `reason`.

**What I learned**

- An API lets the app communicate with an external service.
- An API key is a private credential used to authenticate a request.
- An API request sends instructions and feedback to the service; an API response brings the result back to the app.
- JSON stores information as named fields and values that Python can read.

**Testing**

- Successfully completed a live OpenAI API call during guided testing.
- Used the fixed comment: “The reporting dashboard takes forever to load.”

**Design decisions**

- Used `gpt-4o-mini` with a strict JSON schema to request predictable output.
- Set a 30-second timeout and disabled automatic retries; added messages for failed requests or unreadable responses.
- Kept this single-comment test separate from the CSV upload while establishing the API connection.

**Data flow**\
App with feedback and taxonomy → API → model → JSON response → app

**Commit**

- `9d50c0d` — Complete Day 6 OpenAI API integration.

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

## Day 8 — Validate Five-Field Structured Output

**What I built**

- Created `prompts/feedback_classification_v3.md`, extending V2 with a summary and confidence score.
- Updated `evaluation/harness.py` to require exactly five fields: `feedback_type`, `product_theme`, `severity`, `summary`, and `confidence`.
- Checked allowed classification values, a text summary, and numeric confidence between 0 and 1. Missing or extra fields and boolean confidence values are rejected.
- Added summary and confidence to evaluation results, documented the output in `README.md`, and improved the incomplete-answer error message.

**What I learned**

- Structured output gives the application a predictable format; validation checks that the response follows it.
- Technical reliability and classification quality are different: a response can be structurally valid while its classification is debatable or incorrect.
- A confidence score describes the model's reported certainty, not a guarantee that the answer is correct.

**Testing**

- Ran the 10-case evaluation against the real API using V3 during guided testing.
- There were no API or schema failures.
- One classification disagreement occurred: D7-03 was expected as Navigation, but the model returned Billing.

**Design decisions**

- Preserved V2's taxonomy and classification guidance while extending the output format in V3.
- Kept evaluation scoring focused on the three classification fields; summary and confidence were validated but not scored for quality.
- Low-confidence review flags remained a future capability.

**Data flow**\
Evaluation comments + V3 prompt → OpenAI → JSON validation → comparison with expected classifications → results, metrics, and evaluation CSV export

**Commits**

- `97626bc` — Add structured five-field LLM output and validation.
- `c85b93a` — Improve incomplete response error message.

## Day 9 — Classify Uploaded Feedback End-to-End

**What I built**

- Extracted reusable `classify_feedback()` and `validate_classification()` helpers in `evaluation/harness.py`; updated evaluation to use them without changing its scoring.
- Added a “Classify feedback” button in `app.py` for validated CSV uploads containing up to 20 records.
- Preserved original columns, row order, and feedback IDs as text, including leading zeros.
- Added the five classification fields plus `classification_status` and `classification_error` to each result.
- Added progress updates, success and failure counts, and a results table.
- Stored completed results in Streamlit session state so they survive app reruns, clearing them when the uploaded content changes or is removed.

**What I learned**

- Reusable functions let evaluation and uploaded-feedback processing share the same classification logic.
- One feedback row currently means one API call.
- Per-row error handling means a failed request keeps its original row and ID, records an error, and allows the remaining feedback to continue.
- Streamlit reruns the script during interaction; session state keeps results available without repeating API calls.

**Testing**

- Mocked API responses to check the refactor against the original evaluation across 20 scenarios using the 10 evaluation cases.
- Ran mocked batch checks for preserved records, IDs and row order; the 1-, 20-, and 21-record boundaries; conflicting output columns; request and validation failures; progress; and session state.
- Python syntax checks and `git diff --check` passed.
- During live end-to-end browser testing, first uploaded 5 records: 5/5 succeeded. Then uploaded 20 records: 20/20 succeeded.
- Verified that feedback IDs F001–F020 remained aligned with their original records. Successful processing does not by itself prove classification accuracy.

**Design decisions**

- Loaded the existing V3 prompt once and used one OpenAI client with the existing model, timeout, and retry settings.
- Processed rows sequentially as an MVP trade-off: simple and easy to debug, but larger datasets would raise latency, cost, and rate-limit considerations.
- Rejected uploads over 20 records without truncating them. The original 30-record sample therefore exceeds this limit.
- Rejected input columns that conflict with output names rather than overwrite original data.
- Left classification fields empty on failed rows and recorded a safe error message. Kept the existing classification validation rules unchanged.

**Data flow**\
CSV upload → input validation → Classify feedback → each row's feedback text + V3 prompt → OpenAI → response validation → original row with classification or error → results DataFrame → session state and display

**Commits**

- `3f526b5` — Refactor reusable LLM classification logic.
- `d0cf0ca` — Add batch feedback classification workflow.

## Day 10 — Add Product Operations Insights

**What I built**

- Added count tables and bar charts for feedback type and product theme.
- Included only successfully classified records in these summaries.

**What I learned**

- Grouping individual classifications into counts makes common feedback categories easier to see.
- Failed classifications should remain visible in the results but should not be counted as valid categories.

**Technical concepts**

- Used pandas filtering and `value_counts()` to count categories.
- Used `st.dataframe()` and `st.bar_chart()` to display the counts.

**Problems and solutions**

- Individual results did not provide an overall picture of the uploaded feedback. Added two category summaries.
- No separate debugging incident is documented in this commit.

**Design decisions**

- Kept insights to simple frequency counts. The charts support review but do not automatically prioritise feedback or weight it by severity.

**Commit**

- `1f3ff78` — Add Day 10 feedback type and product theme counts and charts.

## Day 11 — Export Results and Improve Upload Guidance

**What I built**

- Added a download button for `analysed_feedback_results.csv`.
- Exported original feedback alongside classification outputs, status and error information.
- Clarified required CSV columns, the existing 20-record limit and appropriate data use.
- Added upload confirmation and clearer completion and partial-failure messages.

**What I learned**

- A downloadable file lets users continue working with the results outside the app.
- Clear instructions and status messages help users understand what to upload and whether processing succeeded.

**Technical concepts**

- Used `to_csv(index=False)` to create a CSV without an extra pandas row-number column.
- Used `st.download_button()` to make the results downloadable.
- Used success, information and warning messages to communicate different outcomes.

**Problems and solutions**

- Classified upload results could be viewed but did not yet have their own download button. Added CSV export.
- Partial failures needed clearer attention. Added a warning directing users to `classification_error`.

**Design decisions**

- Kept failed rows in the export so users can identify what needs attention.
- Used CSV export without adding persistent storage or external integrations.

**Commit**

- `dcda47e` — Complete Day 11 results export and upload guidance.

## Day 12 — Evaluate and Improve Classification

**What I built**

- Added a manually labelled 20-case evaluation dataset and matching uploadable CSV.
- Connected the evaluation interface to the new dataset.
- Created V4 with a targeted rule for slow but functioning features.
- Switched uploaded-feedback classification from V3 to V4 and documented development results.

**What I learned**

- Comparing model answers with expected labels helps identify specific classification mistakes.
- A targeted prompt change can address an observed error without changing the model or output structure.
- Accuracy on a small evaluation set does not establish accuracy on unseen feedback.

**Technical concepts**

- Extended the existing evaluation workflow with a larger labelled dataset.
- Compared prompt versions using per-field accuracy.
- Kept missing expected labels unscored rather than inventing answers.

**Problems and solutions**

- The recorded V3 results classified slow or degraded performance as `Bug` when it should be `Usability Issue`.
- V4 clarified that slowness alone is not a bug when the functionality still works.
- The new dataset has no expected severity labels, so severity remains “Not scored”.

**Recorded development results**

| Prompt | Feedback type | Product theme |
|---|---|---|
| V3 | 18/20 — 90% | 20/20 — 100% |
| V4 | 20/20 — 100% | 20/20 — 100% |

These figures are recorded in the README; complete historical response exports are not stored in the repository.

**Design decisions**

- Preserved earlier prompts and kept the model and five-field schema unchanged.
- Used a small, fixed dataset for focused comparison; summary and confidence were not scored for quality.

**Commits**

- `84f7af5` — Day 12: evaluate classifier and improve prompt accuracy.
- `2e4c970` — Document Day 12 evaluation results.

## Day 13 — Align the Classifier and Prepare the MVP for Use

**What I built**

- Defined one active V4 prompt shared by upload classification and evaluation.
- Removed the prompt dropdown, added missing-prompt protection and cleared evaluation results belonging to another prompt version.
- Created `demo_feedback.csv` with F001–F020 while preserving the original sample.
- Simplified the interface into Upload → Classify → Results → Insights → Download, with evaluation below the main workflow.
- Moved supporting information into expanders while keeping classified results and evaluation metrics visible.
- Updated the README with current functionality and local setup instructions.
- Added `.DS_Store` to `.gitignore`.

**What I learned**

- Shared configuration prevents two parts of an app from accidentally using different versions.
- Results should clearly correspond to the classifier being evaluated.
- A demo file should satisfy the app’s own input rules.
- Clear page structure and optional detail can make an app easier to use without changing its processing behaviour.

**Technical concepts**

- Used one prompt path as the shared configuration.
- Used session-state checks to remove outdated evaluation results.
- Used Streamlit containers for page placement, expanders for supporting detail and columns for charts.
- Used `.gitignore` to exclude unnecessary operating-system files.

**Problems and solutions**

- Evaluation defaulted to V1 because the dropdown used the first sorted filename, while upload classification used V4. Replaced the independent choices with one V4 setting.
- The original 30-record sample exceeded the intentional limit. Added a separate 20-record demo instead of changing the limit or deleting historical examples.
- The interface contained lengthy guidance and development-oriented wording. Shortened the text, separated the main workflow and made evaluation secondary.
- The README still described parts of the app as future work and referred to V3 as current. Updated it to match the implementation.

**Design decisions**

- Retained V1–V3 as historical files, but removed prompt comparison from the normal user interface.
- Preserved the original sample for demonstrating oversized-upload validation.
- Kept detailed information accessible in expanders.
- Left classification, evaluation calculations and the 20-record limit unchanged. Deployment preparation is complete; deployment itself has **not yet been completed**.

**Commits**

- `b1ae832` — Use shared V4 prompt for evaluation and classification.
- `6dda0fd` — Add valid 20-record deployment demo CSV.
- `2037ead` — Ignore macOS DS_Store files.
- `5cc436d` — Simplify Streamlit layout and user guidance.
- `40fc52d` — Update README for current MVP.
