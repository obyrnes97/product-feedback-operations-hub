# Product Feedback Operations Hub

AI-assisted MVP that turns unstructured customer feedback into structured product insights.

## MVP Goal

Turn unstructured customer feedback from sources such as Slack, support conversations, and customer-facing teams into structured product insights that a Product Operations or Product team can review and prioritise.

## MVP Scope

The MVP will:

- Accept customer feedback from a CSV file.
- Process individual feedback items.
- Classify feedback by feedback type, product theme, and severity.
- Use an LLM API for AI-assisted classification.
- Display the structured results in a simple Streamlit interface.
- Provide simple summary charts or metrics.
- Allow the structured results to be downloaded.

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

## Non-Goals

For this MVP, we will not:

- Build direct integrations with Slack, CRM, support platforms, or other customer feedback systems. Feedback will initially be provided via CSV.
- Build user authentication or permissions.
- Build a production database or persistent storage.
- Automatically create or update tickets in other systems.
- Build complex analytics or reporting.
- Train or fine-tune our own machine-learning model.
- Build a production-ready enterprise application.

## Tech Stack

- Python
- Streamlit
- Pandas
- LLM API
- GitHub
