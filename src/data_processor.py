"""Data processing utilities for the Revenue Analytics Dashboard."""

import pandas as pd
import streamlit as st
from src.config import GEOGRAPHIC_COLUMNS

@st.cache_data
def process_data(df):
    """Process the dataframe for analysis."""
    df = df.copy()
    
    # Convert date features
    df['_weekday'] = df['date'].dt.dayofweek
    df['_day'] = df['date'].dt.day
    df['_month'] = df['date'].dt.month
    df['_year'] = df['date'].dt.year
    df['_visitHour'] = pd.to_datetime(df['visitStartTime'], unit='s').dt.hour
    
    # Handle categorical variables except geographic columns
    for col in df.columns:
        if col not in GEOGRAPHIC_COLUMNS and col != 'date':
            if df[col].dtype == 'object':
                try:
                    df[col] = pd.to_numeric(df[col])
                except:
                    df[col] = df[col].astype('category').cat.codes
    
    # Fill missing values
    for col in df.columns:
        if col in GEOGRAPHIC_COLUMNS:
            df[col] = df[col].fillna('Unknown')
        else:
            df[col] = df[col].fillna(-1)
    
    return df