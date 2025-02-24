"""Data loading utilities for the Revenue Analytics Dashboard."""

import pandas as pd
import streamlit as st
from src.config import DATA_PATH

@st.cache_data
def load_data():
    """Load and cache the dataset."""
    try:
        df = pd.read_csv(DATA_PATH)
        df['date'] = pd.to_datetime(df['date'])
        return df
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None