import json
import os
from pathlib import Path

import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI, OpenAIError

load_dotenv(Path(__file__).resolve().parent / ".env")

st.set_page_config(page_title="Product Feedback Operations Hub")

st.title("Product Feedback Operations Hub")

if os.getenv("OPENAI_API_KEY", "").strip():
    st.success("OpenAI API key is loaded.")
else:
    st.warning("OpenAI API key is not set. Add it to your local .env file.")

st.subheader("LLM classification test")
test_feedback = "The reporting dashboard takes forever to load."
st.write(test_feedback)

if st.button("Test LLM classification"):
    if not os.getenv("OPENAI_API_KEY", "").strip():
        st.warning("Add OPENAI_API_KEY to your local .env file before testing.")
    else:
        try:
            readme = Path(__file__).with_name("README.md").read_text(encoding="utf-8")
            taxonomy = readme.split("## Feedback Taxonomy\n", 1)[1].split("\n## ", 1)[0]
            allowed_values = {
                "feedback_type": ["Feature Request", "Usability Issue", "Bug", "Positive Feedback", "Other"],
                "product_theme": ["Onboarding", "Performance", "Navigation", "Reporting", "Integrations", "Billing", "Permissions", "Reliability", "Other"],
                "severity": ["High", "Medium", "Low"],
            }
            schema = {
                "type": "object",
                "properties": {
                    **{name: {"type": "string", "enum": values} for name, values in allowed_values.items()},
                    "reason": {"type": "string"},
                },
                "required": [*allowed_values, "reason"],
                "additionalProperties": False,
            }
            with st.spinner("Classifying test feedback..."):
                with OpenAI(max_retries=0, timeout=30.0) as client:
                    response = client.responses.create(
                        model="gpt-4o-mini",
                        instructions=(
                            "Classify the feedback using the README taxonomy below as the source of truth. "
                            "Return exactly feedback_type, product_theme, severity, and a short reason "
                            "(one sentence) as JSON. Use only the allowed classification values. "
                            "If feedback_type or product_theme cannot be reliably classified, use Other "
                            "rather than guessing. Do not infer unstated workflow impact.\n\n" + taxonomy
                        ),
                        input=test_feedback,
                        text={"format": {
                            "type": "json_schema", "name": "feedback_classification",
                            "strict": True, "schema": schema,
                        }},
                        store=False,
                    )
            if response.status != "completed" or not response.output_text:
                st.warning("The model did not return a complete classification. Please try again.")
            else:
                classification = json.loads(response.output_text)
                st.json(classification)
        except OpenAIError as error:
            st.error("The OpenAI request failed.")
            st.json({
                "category": type(error).__name__,
                "http_status": getattr(error, "status_code", None),
                "error_code": getattr(error, "code", None),
                "error_type": getattr(error, "type", None),
            })
        except (OSError, IndexError, ValueError):
            st.error("Could not read the README taxonomy or parse the classification.")

uploaded_file = st.file_uploader("Upload customer feedback", type=["csv"])
st.caption(
    "Expected CSV columns: `feedback_id`, `date`, `feedback_text`, "
    "`customer_type`, `source`, and `product_area`."
)

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
    except pd.errors.EmptyDataError:
        st.error(
            "The uploaded CSV has no data or headers. "
            "Please add the required column headers and at least one feedback record."
        )
        st.stop()
    required_columns = [
        "feedback_id",
        "date",
        "feedback_text",
        "customer_type",
        "source",
        "product_area",
    ]
    missing_columns = [column for column in required_columns if column not in df.columns]

    if missing_columns:
        st.error(f"Missing required columns: {', '.join(missing_columns)}")
    elif df.empty:
        st.error("The uploaded CSV is empty. Please add at least one feedback record.")
    else:
        blank_feedback = df["feedback_text"].fillna("").astype(str).str.strip().eq("")
        if blank_feedback.any():
            affected_ids = df.loc[blank_feedback, "feedback_id"].astype(str)
            st.error(
                "feedback_text cannot be blank. "
                f"Affected feedback_id values: {', '.join(affected_ids)}"
            )
        else:
            duplicate_feedback = df["feedback_id"].duplicated(keep=False)
            if duplicate_feedback.any():
                duplicated_ids = df.loc[
                    duplicate_feedback, "feedback_id"
                ].drop_duplicates().astype(str)
                st.error(
                    "feedback_id values must be unique. "
                    f"Duplicated ID values: {', '.join(duplicated_ids)}"
                )
            else:
                st.dataframe(df)
