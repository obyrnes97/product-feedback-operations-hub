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
