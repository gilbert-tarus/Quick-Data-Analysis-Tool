import streamlit as st
import pandas as pd
import new_analyze_function as analyze_function

st.set_page_config(page_title="New Quick Data Analysis Tool", layout="wide")

# Load CSS
def load_css(css_str):
    st.markdown(f"<style>{css_str}</style>", unsafe_allow_html=True)

with open("static/styles.css") as f:
    load_css(f.read())

with open("static/results_styles.css") as f:
    load_css(f.read())

st.title("New Quick Data Analysis Tool")

try:
    # Upload
    if "df" not in st.session_state:
        uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])
        if uploaded_file:
            st.session_state.df = pd.read_csv(uploaded_file)
            st.session_state.columns = st.session_state.df.columns.tolist()
            st.session_state.agg_fields = []
            st.rerun()
        else:
            st.stop()
    
    df = st.session_state.df
    columns = st.session_state.columns
    
    st.write("### Preview")
    st.dataframe(df.head())
    
    # Group By
    st.subheader("Group By Column")
    st.session_state.group_by_col = st.selectbox("Select Group By Column", columns)
    
    # Aggregation Fields
    st.subheader("Aggregation Fields")
    available_for_agg = [c for c in columns if c != st.session_state.group_by_col]
    
    for idx, (field, agg_type) in enumerate(st.session_state.agg_fields):
        cols_buttons = st.columns([1, 1, 3, 3, 1])
        with cols_buttons[0]:
            if st.button("↑", key=f"up_{idx}") and idx > 0:
                st.session_state.agg_fields[idx], st.session_state.agg_fields[idx - 1] = \
                    st.session_state.agg_fields[idx - 1], st.session_state.agg_fields[idx]
                st.rerun()
        with cols_buttons[1]:
            if st.button("↓", key=f"down_{idx}") and idx < len(st.session_state.agg_fields) - 1:
                st.session_state.agg_fields[idx], st.session_state.agg_fields[idx + 1] = \
                    st.session_state.agg_fields[idx + 1], st.session_state.agg_fields[idx]
                st.rerun()
        with cols_buttons[2]:
            st.session_state.agg_fields[idx] = (
                st.selectbox(f"Field {idx + 1}", available_for_agg, index=available_for_agg.index(field)),
                agg_type
            )
        with cols_buttons[3]:
            st.session_state.agg_fields[idx] = (
                st.session_state.agg_fields[idx][0],
                st.selectbox(f"Type {idx + 1}", ["first", "sum", "mean", "count", "max", "min", "nunique"],
                             index=["first", "sum", "mean", "count", "max", "min", "nunique"].index(agg_type))
            )
        with cols_buttons[4]:
            if st.button("✕", key=f"remove_{idx}"):
                st.session_state.agg_fields.pop(idx)
                st.rerun()
    
    if st.button("Add Aggregation Field"):
        if available_for_agg:  # only add if available columns exist
            st.session_state.agg_fields.append((available_for_agg[0], "sum"))
            st.rerun()
    
    #  Analysis Options
    with st.form("analysis_form"):
        sort_by_options = [f for f, _ in st.session_state.agg_fields] or columns
        sort_by_col = st.selectbox("Sort By Column", sort_by_options)
    
        top_n = st.number_input("Top N", min_value=1, value=10)
        display_mode = st.selectbox("Display Mode", ["some", "all", "None"])
        csv_filename = st.text_input("Output CSV Filename", "analysis_result.csv")
    
        analyze_btn = st.form_submit_button("Analyze")
        reset_btn = st.form_submit_button("Reset")
    
    # Reset
    if reset_btn:
        for key in ["df", "columns", "agg_fields", "group_by_col"]:
            st.session_state.pop(key, None)
        st.rerun()
    
    # Run Analysis
    if analyze_btn:
        aggs_dict = {field: agg for field, agg in st.session_state.agg_fields}
        html_output = analyze_function.analyze_top_fields(
            nil_importers=df,
            group_by_cols=[st.session_state.group_by_col],
            agg_dict=aggs_dict,
            sort_by=[sort_by_col],
            top_n=top_n,
            csv_filename=csv_filename,
            empty_fields=None,
            display_mode=display_mode
        )
    
        st.markdown(html_output, unsafe_allow_html=True)
    
        try:
            result_df = pd.read_html(html_output)[0]
            csv_bytes = result_df.to_csv(index=False).encode("utf-8")
            st.download_button("Download CSV", data=csv_bytes, file_name=csv_filename, mime="text/csv")
        except Exception as e:
            st.error(f"Could not parse HTML: {e}")
except Exception as new_e:
    st.error(f'Sorry! {new_e}')