import hashlib
import os
from io import BytesIO
from pathlib import Path

import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI, OpenAIError

from evaluation.harness import classify_feedback, field_accuracy, run_evaluation

load_dotenv(Path(__file__).resolve().parent / ".env")

st.set_page_config(page_title="Product Feedback Operations Hub")

st.title("Product Feedback Operations Hub")

if os.getenv("OPENAI_API_KEY", "").strip():
    st.success("OpenAI API key is loaded.")
else:
    st.warning("OpenAI API key is not set. Add it to your local .env file.")

st.subheader("Day 12 prompt evaluation")
st.caption("Run the fixed 20 test comments. One API call per case; expected answers stay local.")
project_dir = Path(__file__).resolve().parent
active_prompt_path = project_dir / "prompts" / "feedback_classification_v4.md"
active_prompt_version = active_prompt_path.stem.rsplit("_", 1)[-1].upper()
prompt_available = active_prompt_path.is_file()
st.caption(f"Evaluating the current classifier: {active_prompt_version}.")
if not prompt_available:
    st.error(
        f"The current classifier prompt ({active_prompt_path.name}) is missing. "
        "Restore it in prompts/ to enable evaluation and feedback classification."
    )

previous_results = st.session_state.get("evaluation_results", [])
if not prompt_available or any(
    row.get("prompt_file") != active_prompt_path.name for row in previous_results
):
    st.session_state.pop("evaluation_results", None)

if st.button("Run evaluation", disabled=not prompt_available):
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
                    active_prompt_path,
                    project_dir / "evaluation" / "day12_evaluation_cases.json",
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
        file_name=f"day12_{Path(results[0]['prompt_file']).stem}_results.csv",
        mime="text/csv",
    )

st.caption("Upload a CSV (.csv) file containing customer feedback. Maximum 20 feedback records.")
st.caption(
    "Required columns: `feedback_id`, `date`, `feedback_text`, "
    "`customer_type`, `source`, and `product_area`."
)
st.caption(
    "Privacy: Do not upload confidential or personally identifiable customer information "
    "unless this application is approved for that data."
)
uploaded_file = st.file_uploader("Upload customer feedback", type=["csv"])

classification_fields = [
    "feedback_type", "product_theme", "severity", "summary", "confidence",
]
output_columns = classification_fields + ["classification_status", "classification_error"]
uploaded_bytes = uploaded_file.getvalue() if uploaded_file is not None else None
upload_key = hashlib.sha256(uploaded_bytes).hexdigest() if uploaded_bytes is not None else None
if st.session_state.get("classification_upload_key") != upload_key:
    st.session_state.pop("classification_results", None)
    st.session_state["classification_upload_key"] = upload_key

if uploaded_file is not None:
    try:
        # Keep original CSV values, including leading zeros and literal "NA" IDs.
        df = pd.read_csv(BytesIO(uploaded_bytes), dtype=str, keep_default_na=False)
    except pd.errors.EmptyDataError:
        st.error(
            "The uploaded CSV has no data or headers. "
            "Please add the required column headers and at least one feedback record."
        )
        st.stop()
    except (pd.errors.ParserError, UnicodeDecodeError):
        st.error("Could not read the CSV. Please upload a valid UTF-8 CSV file.")
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
    conflicting_columns = [column for column in output_columns if column in df.columns]

    if missing_columns:
        st.error(f"Missing required columns: {', '.join(missing_columns)}")
    elif df.empty:
        st.error("The uploaded CSV is empty. Please add at least one feedback record.")
    elif len(df) > 20:
        st.error(f"The CSV contains {len(df)} records. Please upload at most 20 records.")
    elif conflicting_columns:
        st.error(
            "CSV columns conflict with classification output columns. "
            f"Please rename these columns: {', '.join(conflicting_columns)}"
        )
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
                st.success(f"Upload successful: **{len(df)}** feedback records uploaded.")
                st.dataframe(df)
                if st.button("Classify feedback", disabled=not prompt_available):
                    st.session_state.pop("classification_results", None)
                    if not os.getenv("OPENAI_API_KEY", "").strip():
                        st.warning("Add OPENAI_API_KEY to your local .env file before classifying.")
                    else:
                        progress = st.progress(0, text="Starting classification...")
                        try:
                            prompt = active_prompt_path.read_text(encoding="utf-8")
                            classified_rows = []
                            with OpenAI(max_retries=0, timeout=30.0) as client:
                                for completed, original_row in enumerate(df.to_dict("records"), start=1):
                                    row = dict(original_row)
                                    row.update({field: None for field in classification_fields})
                                    row.update(classification_status="Success", classification_error="")
                                    try:
                                        row.update(classify_feedback(client, prompt, original_row["feedback_text"]))
                                    except OpenAIError as error:
                                        row.update(
                                            classification_status="Error",
                                            classification_error=f"OpenAI request failed ({type(error).__name__}).",
                                        )
                                    except ValueError:
                                        row.update(
                                            classification_status="Error",
                                            classification_error="The model returned an invalid or incomplete classification.",
                                        )
                                    classified_rows.append(row)
                                    progress.progress(
                                        completed / len(df),
                                        text=f"Processed {completed} of {len(df)} feedback records",
                                    )
                            st.session_state["classification_results"] = pd.DataFrame(
                                classified_rows, columns=[*df.columns, *output_columns]
                            )
                        except (OSError, ValueError, OpenAIError) as error:
                            st.error(
                                f"Could not complete classification: {type(error).__name__}. "
                                f"Check the {active_prompt_version} prompt file and API configuration."
                            )
                        finally:
                            progress.empty()

                classification_results = st.session_state.get("classification_results")
                if classification_results is not None:
                    failed = int((classification_results["classification_status"] == "Error").sum())
                    st.info(
                        f"Classification complete: **{len(classification_results) - failed}** records successfully processed; "
                        f"**{failed}** records failed."
                    )
                    if failed > 0:
                        st.warning(
                            "Some records could not be classified. "
                            "Review the `classification_error` column for details."
                        )
                    st.dataframe(classification_results)
                    st.download_button(
                        "Download results",
                        data=classification_results.to_csv(index=False),
                        file_name="analysed_feedback_results.csv",
                        mime="text/csv",
                    )

                    feedback_type_counts = (
                        classification_results.loc[
                            classification_results["classification_status"] == "Success",
                            "feedback_type",
                        ]
                        .value_counts()
                        .rename_axis("feedback_type")
                        .reset_index(name="count")
                    )
                    st.caption("Classified feedback counts by feedback type")
                    st.dataframe(feedback_type_counts, hide_index=True)
                    st.bar_chart(feedback_type_counts, x="feedback_type", y="count")

                    product_theme_counts = (
                        classification_results.loc[
                            classification_results["classification_status"] == "Success",
                            "product_theme",
                        ]
                        .value_counts()
                        .rename_axis("product_theme")
                        .reset_index(name="count")
                    )
                    st.caption("Classified feedback counts by product theme")
                    st.dataframe(product_theme_counts, hide_index=True)
                    st.bar_chart(product_theme_counts, x="product_theme", y="count")
