"""Device and browser analytics module."""
import plotly.express as px
import streamlit as st
import time
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

@st.cache_data
def analyze_device_metrics(df):
    """Analyze device and browser related metrics."""
    try:
        start_time = time.time()
        logger.info("Starting device metrics analysis")
        logger.debug(f"Input dataframe shape: {df.shape}")

        # Analyze browser usage
        logger.debug("Calculating browser usage statistics")
        browser_usage = df['device.browser'].value_counts().head(10)
        logger.info(f"Top browser count: {len(browser_usage)}")
        logger.debug(f"Most common browser: {browser_usage.index[0]} ({browser_usage.values[0]} uses)")

        # Analyze OS usage
        logger.debug("Calculating operating system usage statistics")
        os_usage = df['device.operatingSystem'].value_counts().head(10)
        logger.info(f"Top OS count: {len(os_usage)}")
        logger.debug(f"Most common OS: {os_usage.index[0]} ({os_usage.values[0]} uses)")

        # Analyze device categories
        logger.debug("Calculating device category statistics")
        device_category = df['device.deviceCategory'].value_counts()
        logger.info(f"Device categories found: {len(device_category)}")
        logger.debug(f"Device category distribution: {device_category.to_dict()}")

        # Analyze mobile usage
        logger.debug("Calculating mobile usage statistics")
        mobile_usage = df['device.isMobile'].value_counts()
        mobile_percentage = (mobile_usage.get(True, 0) / len(df)) * 100
        logger.info(f"Mobile usage percentage: {mobile_percentage:.2f}%")

        # Calculate revenue metrics
        logger.debug("Calculating revenue metrics by device")
        avg_revenue_by_device = df.groupby('device.deviceCategory')['totals.transactionRevenue'].mean()
        logger.info("Average revenue by device category calculated")
        logger.debug(f"Revenue by device: {avg_revenue_by_device.to_dict()}")

        # Calculate pageview metrics
        logger.debug("Calculating pageview metrics by device")
        avg_pageviews_by_device = df.groupby('device.deviceCategory')['totals.pageviews'].mean()
        logger.info("Average pageviews by device category calculated")
        logger.debug(f"Pageviews by device: {avg_pageviews_by_device.to_dict()}")

        metrics = {
            'browser_usage': browser_usage,
            'os_usage': os_usage,
            'device_category': device_category,
            'mobile_usage': mobile_usage,
            'avg_revenue_by_device': avg_revenue_by_device,
            'avg_pageviews_by_device': avg_pageviews_by_device
        }

        execution_time = time.time() - start_time
        logger.info(f"Device metrics analysis completed in {execution_time:.2f} seconds")
        return metrics

    except Exception as e:
        logger.error("Error in device metrics analysis", exc_info=True)
        raise

def show_device_analytics(df):
    """Display device and browser analytics."""
    try:
        start_time = time.time()
        logger.info("Starting device analytics visualization")
        
        st.header("📱 Device & Browser Analytics")
        
        # Get device metrics
        logger.debug("Retrieving device metrics")
        device_stats = analyze_device_metrics(df)
        
        col1, col2 = st.columns(2)
        
        with col1:
            try:
                logger.debug("Creating device category distribution visualization")
                st.subheader("Device Category Distribution")
                fig = px.pie(
                    values=device_stats['device_category'].values,
                    names=device_stats['device_category'].index,
                    title="Traffic by Device Category"
                )
                st.plotly_chart(fig)
                logger.info("Device category distribution chart created successfully")
            except Exception as e:
                logger.error("Error creating device category chart", exc_info=True)
                st.error("Error displaying device category distribution")
            
            try:
                logger.debug("Creating operating system usage visualization")
                st.subheader("Operating System Usage")
                fig = px.bar(
                    x=device_stats['os_usage'].index,
                    y=device_stats['os_usage'].values,
                    title="Top Operating Systems"
                )
                st.plotly_chart(fig)
                logger.info("Operating system usage chart created successfully")
            except Exception as e:
                logger.error("Error creating OS usage chart", exc_info=True)
                st.error("Error displaying operating system usage")
        
        with col2:
            try:
                logger.debug("Creating average revenue by device visualization")
                st.subheader("Average Revenue by Device")
                fig = px.bar(
                    x=device_stats['avg_revenue_by_device'].index,
                    y=device_stats['avg_revenue_by_device'].values,
                    title="Average Revenue by Device Category"
                )
                st.plotly_chart(fig)
                logger.info("Average revenue by device chart created successfully")
            except Exception as e:
                logger.error("Error creating revenue by device chart", exc_info=True)
                st.error("Error displaying revenue by device")
            
            try:
                logger.debug("Creating browser usage visualization")
                st.subheader("Browser Usage")
                fig = px.bar(
                    x=device_stats['browser_usage'].index,
                    y=device_stats['browser_usage'].values,
                    title="Top Browsers"
                )
                st.plotly_chart(fig)
                logger.info("Browser usage chart created successfully")
            except Exception as e:
                logger.error("Error creating browser usage chart", exc_info=True)
                st.error("Error displaying browser usage")

        execution_time = time.time() - start_time
        logger.info(f"Device analytics visualization completed in {execution_time:.2f} seconds")

    except Exception as e:
        logger.error("Error in device analytics visualization", exc_info=True)
        st.error("An error occurred while displaying device analytics")
