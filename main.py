"""Main Streamlit application file for the Revenue Analytics Dashboard."""

import streamlit as st
import pandas as pd
import numpy as np
from src.config import PAGE_CONFIG, DATA_PATH, GDRIVE_FILE_ID
import gdown
import os
from src.data_loader import load_data
from src.data_processor import process_data
from src.analytics.device_analytics import show_device_analytics
from src.analytics.traffic_analytics import show_traffic_analytics
from src.analytics.visit_analytics import show_visit_patterns
from src.analytics.geographic_analytics import show_geographic_insights
from src.analytics.customer_analytics import show_advanced_customer_segmentation, identify_high_value_customers
from src.modeling.predictor import show_prediction_interface
from src.utils.visualization import (
    create_metric_card,
    create_time_series,
    format_currency,
    format_percentage,
    format_number
)

# Set page configuration
st.set_page_config(**PAGE_CONFIG)


import os
import gdown
import zipfile
import streamlit as st
from src.config import GDRIVE_FILE_ID, DATA_PATH, EXTRACT_DIR

# Ensure necessary directories exist
if not os.path.exists(EXTRACT_DIR):
    os.makedirs(EXTRACT_DIR)

def download_file():
    """Download the ZIP file from Google Drive if not already downloaded."""
    if not os.path.exists(DATA_PATH):
        st.info("🔽 Downloading dataset...")
        gdown.download(f"https://drive.google.com/uc?id={GDRIVE_FILE_ID}", DATA_PATH, quiet=False)
    
    if os.path.exists(DATA_PATH):
        st.success("✅ File downloaded successfully.")
    else:
        st.error("❌ Download failed.")
        return False
    return True

def extract_file():
    """Extract the downloaded ZIP file."""
    if os.path.exists(EXTRACT_DIR) and len(os.listdir(EXTRACT_DIR)) > 0:
        st.success("✅ Data is already extracted.")
        return  # Skip extraction if already done

    try:
        with zipfile.ZipFile(DATA_PATH, 'r') as zip_ref:
            zip_ref.extractall(EXTRACT_DIR)
        st.success(f"✅ File extracted to: {EXTRACT_DIR}")
    except zipfile.BadZipFile:
        st.error("❌ Error: File is not a valid ZIP archive.")

# Ensure the dataset is available before running the dashboard
if download_file():
    extract_file()





def show_overview(df):
    """Display overview page with key metrics."""
    st.header("📊 Overview")
    
    # Calculate key metrics
    total_revenue = df['totals.transactionRevenue'].sum()
    total_visits = len(df)
    avg_revenue_per_visit = total_revenue / total_visits
    bounce_rate = (df['totals.bounces'].sum() / total_visits) * 100
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Revenue", format_currency(total_revenue))
    col2.metric("Total Visits", format_number(total_visits))
    col3.metric("Avg Revenue per Visit", format_currency(avg_revenue_per_visit))
    col4.metric("Bounce Rate", format_percentage(bounce_rate))
    
    # Revenue trends
    st.subheader("Revenue Trends")
    daily_revenue = df.groupby('date')['totals.transactionRevenue'].sum().reset_index()
    fig = create_time_series(
        daily_revenue,
        x='date',
        y='totals.transactionRevenue',
        title='Daily Revenue Trends'
    )
    st.plotly_chart(fig)

def main():
    """Main application function."""
    st.title("🎯 Revenue Analytics Dashboard")
    
    # Initialize session state
    if 'model_trained' not in st.session_state:
        st.session_state.model_trained = False
    
    # Sidebar navigation
    page = st.sidebar.selectbox(
        "Select Page",
        ["Overview", "Device Analytics", "Traffic Sources", "Visit Patterns", 
         "Revenue Prediction", "Customer Segmentation", "Geographic Insights"],
        key="page_navigation"  # Added unique key
         
    )
    
    # Load data
    df = load_data()
    if df is None:
        return
    
    # # Page routing
    # pages = {
    #     "Overview": lambda: show_overview(df),
    #     "Device Analytics": lambda: show_device_analytics(df),
    #     "Traffic Sources": lambda: show_traffic_analytics(df),
    #     "Visit Patterns": lambda: show_visit_patterns(df),
    #     "Revenue Prediction": lambda: show_prediction_interface(df),
    #     "Customer Segmentation": lambda: show_advanced_customer_segmentation(df),
    #     "Geographic Insights": lambda: show_geographic_insights(df)
    # }
    
    # # Display selected page
    # pages[page]()



    
    # Page routing
    if page == "Overview":
        show_overview(df)
    elif page == "Device Analytics":
        show_device_analytics(df)
    elif page == "Traffic Sources":
        show_traffic_analytics(df)
    elif page == "Visit Patterns":
        show_visit_patterns(df)
    elif page == "Revenue Prediction":
        show_prediction_interface(df)
    elif page == "Customer Segmentation":
        # Use the new advanced segmentation
        show_advanced_customer_segmentation(df)
        
        # Option to view the legacy segmentation
        if st.checkbox("Show Legacy Segmentation Method"):
            st.header("👥 Legacy Customer Segmentation")
            
            # Get customer segments
            segments = identify_high_value_customers(df)
            
            # Show segment statistics
            for segment, customers in segments.items():
                segment_revenue = df[
                    df['visitNumber'].isin(customers)
                ]['totals.transactionRevenue'].sum()
                
                st.subheader(f"{segment.title()} Value Customers")
                col1, col2 = st.columns(2)
                col1.metric("Number of Customers", len(customers))
                col2.metric("Total Revenue", f"${segment_revenue:,.2f}")
            
            # Show customer details
            selected_segment = st.selectbox(
                "Select Legacy Segment to View Customers",
                ["High", "Medium", "Low"]
            )
            
            segment_customers = df[
                df['visitNumber'].isin(segments[selected_segment.lower()])
            ].groupby('visitNumber').agg({
                'totals.transactionRevenue': 'sum',
                'totals.pageviews': 'sum'
            }).reset_index()
            
            st.dataframe(segment_customers)
    elif page == "Geographic Insights":
        show_geographic_insights(df)

if __name__ == "__main__":
    main()


