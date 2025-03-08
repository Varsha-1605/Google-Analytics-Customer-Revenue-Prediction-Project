# """Data loading utilities for the Revenue Analytics Dashboard."""
# import os
# import zipfile
# import pandas as pd
# import streamlit as st
# from src.config import DATA_PATH, EXTRACT_DIR

# @st.cache_data
# def load_data():
#     """Load and cache the dataset."""
#     try:
#         if DATA_PATH.endswith(".zip"):  
#             # Ensure the extraction folder exists
#             if not os.path.exists(EXTRACT_DIR):
#                 os.makedirs(EXTRACT_DIR)

#             # Extract ZIP file
#             with zipfile.ZipFile(DATA_PATH, 'r') as zip_ref:
#                 zip_ref.extractall(EXTRACT_DIR)

#             # Automatically find the extracted CSV file
#             extracted_files = os.listdir(EXTRACT_DIR)
#             csv_files = [f for f in extracted_files if f.endswith(".csv")]

#             if not csv_files:
#                 st.error("No CSV file found in the extracted ZIP.")
#                 return None

#             csv_path = os.path.join(EXTRACT_DIR, csv_files[0])  # Pick the first CSV file
#         else:
#             csv_path = DATA_PATH  # Direct CSV file

#         # Load the dataset
#         df = pd.read_csv(csv_path)
#         df['date'] = pd.to_datetime(df['date'])
#         return df
#     except Exception as e:
#         st.error(f"Error loading data: {str(e)}")
#         return None









import os
import zipfile
import pandas as pd
import logging
import streamlit as st
from src.utils.logger import setup_logger
from src.config import DATA_PATH, EXTRACT_DIR

logger = setup_logger(__name__)

@st.cache_data
def load_data():
    """Load and cache the dataset."""
    try:
        logger.info("Starting data loading process")
        if DATA_PATH.endswith(".zip"):
            logger.info(f"Processing ZIP file: {DATA_PATH}")
            if not os.path.exists(EXTRACT_DIR):
                logger.info(f"Creating extraction directory: {EXTRACT_DIR}")
                os.makedirs(EXTRACT_DIR)

            with zipfile.ZipFile(DATA_PATH, 'r') as zip_ref:
                logger.info("Extracting ZIP file")
                zip_ref.extractall(EXTRACT_DIR)

            extracted_files = os.listdir(EXTRACT_DIR)
            csv_files = [f for f in extracted_files if f.endswith(".csv")]
            
            if not csv_files:
                logger.error("No CSV file found in the extracted ZIP")
                st.error("No CSV file found in the extracted ZIP.")
                return None

            csv_path = os.path.join(EXTRACT_DIR, csv_files[0])
            logger.info(f"Loading CSV file: {csv_path}")
        else:
            csv_path = DATA_PATH

        df = pd.read_csv(csv_path)
        df['date'] = pd.to_datetime(df['date'])
        logger.info(f"Data loaded successfully. Shape: {df.shape}")
        return df

    except Exception as e:
        logger.error(f"Error loading data: {str(e)}", exc_info=True)
        st.error(f"Error loading data: {str(e)}")
        return None