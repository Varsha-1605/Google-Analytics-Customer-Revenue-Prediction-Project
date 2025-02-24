"""Data loading utilities for the Revenue Analytics Dashboard."""

# import pandas as pd
# import streamlit as st
# from src.config import DATA_PATH

# @st.cache_data
# def load_data():
#     """Load and cache the dataset."""
#     try:
#         df = pd.read_csv(DATA_PATH)
#         df['date'] = pd.to_datetime(df['date'])
#         return df
#     except Exception as e:
#         st.error(f"Error loading data: {str(e)}")
#         return None


import pandas as pd
import streamlit as st
from src.config import DATA_PATH

@st.cache_data
def load_data():
    """Load and cache the dataset."""
    try:
        if DATA_PATH.endswith(".zip"):
            with zipfile.ZipFile(DATA_PATH, 'r') as zip_ref:
                zip_ref.extractall(EXTRACT_DIR)
            csv_path = f"{EXTRACT_DIR}/your_dataset.csv"
        else:
            csv_path = DATA_PATH  # Assume it's a CSV

        df = pd.read_csv(csv_path)
        df['date'] = pd.to_datetime(df['date'])
        return df
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None
