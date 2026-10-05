# Product Feedback Operations Hub

AI-assisted MVP that turns unstructured customer feedback into structured product insights.

## MVP Goal

Turn unstructured customer feedback from sources such as Slack, support conversations, and customer-facing teams into structured product insights that a Product Operations or Product team can review and prioritise.

## MVP Scope

The MVP uses Streamlit and the OpenAI API to classify uploaded customer feedback with `gpt-4o-mini` and the active V4 prompt. Each feedback item is processed sequentially in one API request, sending its feedback text and the classification instructions.

## User flow

**Upload → Classify → Results → Insights → Download**

1. **Upload:** Choose a CSV and optionally expand the raw-data preview.
2. **Classify:** Click **Classify feedback** and follow progress as each record is processed.
3. **Results:** Review the visible results table and success/failure totals. Original columns, row order and text IDs are preserved.
4. **Insights:** Explore two Product Operations bar charts showing counts by feedback type and product theme. Only successful classifications are counted; count tables are available in an expander.
5. **Download:** Export `analysed_feedback_results.csv`, containing the original data, five classification outputs, `classification_status` and `classification_error`, including any failed rows.

Completed results remain available during ordinary app reruns and clear when the uploaded content changes or is removed. **AI Classification Evaluation** is an optional secondary workflow below the main workflow.

## CSV input

Upload a UTF-8 CSV containing **1–20 feedback records** with these columns:

`feedback_id`, `date`, `feedback_text`, `customer_type`, `source`, `product_area`

Uploads over 20 records are **rejected, not truncated**. The app also rejects empty or unreadable files, missing required columns, blank feedback text, duplicate feedback IDs and columns that conflict with classification output names. Use sample or approved customer data.

### Example files

- `demo_feedback.csv`: a valid 20-record example containing F001–F020 from the original sample, with the same columns and values. Start here to test the app.
- `sample_feedback.csv`: 30 records, useful for demonstrating maximum-record validation.
- `evaluation_test_data.csv`: an uploadable CSV containing the same feedback as the current 20-case evaluation dataset.

## Local setup

From the repository directory, create and activate a Python virtual environment, then install the dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

On Windows, activate with `.venv\Scripts\activate` instead. Create a `.env` file in the repository root with your own OpenAI API key:

```dotenv
OPENAI_API_KEY=your_api_key_here
```

Run the app:

```bash
python -m streamlit run app.py
```

The app loads `OPENAI_API_KEY` from the environment or local `.env`. `.env` and `.streamlit/secrets.toml` are excluded from Git by `.gitignore`; never commit API keys or put them in source code. If the key is missing, the app shows a configuration error and does not make classification or evaluation requests.

## Feedback Taxonomy

### `feedback_type`

- **Feature Request:** Functionality that does not currently exist and that the user is requesting to be added or built.
- **Usability Issue:** Existing functionality works, but is difficult to find, understand, navigate, or use effectively.
- **Bug:** Existing functionality does not behave as intended or fails to work.
- **Positive Feedback:** Feedback expressing satisfaction with an existing feature, experience, or aspect of the product.
- **Other:** Feedback that does not clearly fit any of the defined feedback types and cannot be reliably classified into another category.

### `product_theme`

Each feedback item must receive exactly one `product_theme` based on the primary issue described. If multiple themes are mentioned, choose the theme representing the main problem.

| Product Theme | Definition |
| --- | --- |
| Onboarding | Feedback relating to getting started with   the product, including initial setup, configuration, guidance, or learning   how to use it for the first time. |
| Performance | Feedback relating to the speed or   responsiveness of the product, including slow loading, delayed actions, slow   downloads, or long processing times. |
| Navigation | Feedback relating to how easily users can   move through the product and find the pages, sections, features, or   information they need. |
| Reporting | Feedback relating to viewing, creating,   exporting, or using reports and the data presented within them. |
| Integrations | Feedback relating to connecting the product   with external systems or services, including setting up, using, or   experiencing issues with those connections. |
| Billing | Feedback relating to subscriptions, pricing,   payments, invoices, charges, or other billing-related processes. |
| Permissions | Feedback relating to what users can access   or do within the product, including roles, access levels, user permissions,   and restrictions. |
| Reliability | Feedback relating to the stability and   consistency of the product or a feature, including crashes, repeated   failures, intermittent problems, or functionality that works inconsistently. |
| Other | Feedback that does not clearly relate to any   of the defined product themes. |

### `severity`

Each feedback item must receive exactly one severity classification.

- **High:** The feedback explicitly states that the issue prevents or seriously disrupts the user from completing an important task or workflow.
- **Medium:** The user can still complete their workflow, but the feedback identifies meaningful difficulty, delay, friction, or a requested capability that would materially improve their experience or workflow.
- **Low:** The feedback has limited impact on the user’s ability to complete their workflow, represents a minor inconvenience, or is positive feedback.

Severity should be determined primarily by user/workflow impact rather than feedback type. A typical feature request should be Medium, but a feature request may be High if the feedback explicitly states that the missing capability prevents or seriously disrupts an important workflow. Positive feedback should be Low.

## Structured LLM Output

Uploaded-feedback classification and evaluation share the active V4 prompt in `prompts/feedback_classification_v4.md`. V1–V3 are retained as historical files. Each response must contain exactly these five fields:

- `feedback_type`: a value from the feedback type taxonomy above.
- `product_theme`: a value from the product theme taxonomy above.
- `severity`: a value from the severity taxonomy above.
- `summary`: a concise one-sentence summary preserving the core issue, request, or sentiment in the customer's feedback.
- `confidence`: a numeric value between 0 and 1 representing the model's confidence in its classification. 1 means very confident; values closer to 0 mean increasingly uncertain.

The application validates each response before using it. It checks that all five fields are present with no extra fields, the classifications use allowed taxonomy values, the summary is a string (text), and confidence is a number within the allowed range. Invalid responses are recorded as errors in both uploaded-feedback and evaluation results.

Structured output gives the application a predictable format to read, display, and export. Validation catches missing fields and invalid values before they are used. These checks make the AI integration more reliable, but do not guarantee that the model's classification is correct.

## Error handling

An API failure or invalid classification is recorded against the affected row while processing continues for the remaining rows. Failed rows retain their original data, leave classification outputs empty and include an error message. Requests have a 30-second timeout and no automatic retries. If the active prompt is missing, both classification and evaluation are disabled.

## AI Classification Evaluation

Click **Run evaluation** to compare the current V4 classifier against 20 manually labelled examples in `evaluation/day12_evaluation_cases.json`. Expected labels stay local and are not sent to the API. Accuracy metrics appear above an expander containing detailed comparisons, scoring information, prompt/model/run metadata and a separate evaluation CSV download.

Feedback type and product theme are scored. **Severity is currently not scored because all 20 cases lack expected severity labels**, so its metric shows “Not scored”. Summary and confidence are validated but are not scored for quality. Failed requests count as non-matches for scored fields. Results from a different prompt version are cleared before display.

### Historical development results

The following scores were recorded during development, not guaranteed for a new run:

| Prompt | Feedback type accuracy | Product theme accuracy |
|---|---|---|
| V3 | 90% (18/20) | 100% (20/20) |
| V4 | 100% (20/20) | 100% (20/20) |

V3 repeatedly classified slow or degraded performance as `Bug` instead of `Usability Issue`. V4 added one targeted rule clarifying that slow performance is a `Usability Issue` when functionality still works. The prompts and test examples remain in the repository; complete historical V3/V4 response exports are not stored.

These results apply only to this small 20-case evaluation set and do not imply 100% accuracy on unseen feedback.

## Non-Goals

The MVP does not include:

- Direct integrations with Slack, CRM, support platforms or other feedback systems; input is via CSV.
- User authentication or permissions.
- A production database or persistent storage.
- Automatic ticket creation or updates in other systems.
- Complex analytics or reporting.
- Training or fine-tuning a model.
- Enterprise production readiness.

## Tech Stack

- Python
- Streamlit
- Pandas
- OpenAI API (`gpt-4o-mini`)
- GitHub
