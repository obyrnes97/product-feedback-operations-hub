import os
from pathlib import Path

import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI, OpenAIError

from evaluation.harness import field_accuracy, run_evaluation

load_dotenv(Path(__file__).resolve().parent / ".env")

st.set_page_config(page_title="Product Feedback Operations Hub")

st.title("Product Feedback Operations Hub")

if os.getenv("OPENAI_API_KEY", "").strip():
    st.success("OpenAI API key is loaded.")
else:
    st.warning("OpenAI API key is not set. Add it to your local .env file.")

st.subheader("Day 7 prompt evaluation")
st.caption("Run the fixed 10 test comments. One API call per case; expected answers stay local.")
project_dir = Path(__file__).resolve().parent
prompt_files = sorted((project_dir / "prompts").glob("feedback_classification_v*.md"))
selected_prompt = st.selectbox(
    "Prompt version", prompt_files, format_func=lambda path: path.name,
    disabled=not prompt_files,
)
if not prompt_files:
    st.warning("No classification prompt files were found in prompts/.")

if st.button("Run evaluation", disabled=not prompt_files):
    if not os.getenv("OPENAI_API_KEY", "").strip():
        st.warning("Add OPENAI_API_KEY to your local .env file before testing.")
    else:
        progress = st.progress(0, text="Starting evaluation...")

        def show_progress(completed, total):
            progress.progress(completed / total, text=f"Completed {completed}/{total} cases")

        try:
            with OpenAI(max_retries=0, timeout=30.0) as client:
                results = run_evaluation(
                    client,
                    selected_prompt,
                    project_dir / "evaluation" / "feedback_cases.json",
                    on_progress=show_progress,
                )
            st.session_state["evaluation_results"] = results
        except (OSError, ValueError, OpenAIError) as error:
            st.error(f"Could not start evaluation: {type(error).__name__}. Check the prompt and test-case files and API configuration.")
        finally:
            progress.empty()

results = st.session_state.get("evaluation_results", [])
if results:
    st.caption(
        f"Displayed run: {results[0]['prompt_file']} | "
        f"Model: {results[0]['model']} | UTC: {results[0]['run_time']}"
    )
    summary = field_accuracy(results)
    for column, (field, counts) in zip(st.columns(3), summary.items()):
        passed, scored = counts["passed"], counts["scored"]
        label = f"{passed}/{scored} ({passed / scored:.0%})" if scored else "Not scored"
        column.metric(field, label)
    st.caption(
        "Null expectations are not scored. Failed requests count as non-matches for scored fields. "
        "Partial means all scored fields match, but at least one field is not scored."
    )
    results_df = pd.DataFrame(results)
    display_df = results_df.drop(columns=["prompt_file", "model", "run_time"]).copy()
    for field in summary:
        display_df[f"expected_{field}"] = display_df[f"expected_{field}"].fillna("Not scored")
    st.dataframe(display_df)
    st.download_button(
        "Download evaluation results (CSV)",
        data=results_df.to_csv(index=False),
        file_name=f"day7_{Path(results[0]['prompt_file']).stem}_results.csv",
        mime="text/csv",
    )

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
