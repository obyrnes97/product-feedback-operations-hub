import pandas as pd
import streamlit as st

st.set_page_config(page_title="Product Feedback Operations Hub")

st.title("Product Feedback Operations Hub")

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
