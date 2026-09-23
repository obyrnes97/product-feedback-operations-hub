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
    df = pd.read_csv(uploaded_file)
    st.dataframe(df)
