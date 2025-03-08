"""Traffic source analytics module."""
import plotly.express as px
import streamlit as st
import time
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

@st.cache_data
def analyze_traffic_sources(df):
    """Analyze traffic sources and campaign performance."""
    try:
        start_time = time.time()
        logger.info("Starting traffic source analysis")
        logger.debug(f"Input dataframe shape: {df.shape}")

        # Analyze channel revenue
        logger.debug("Calculating channel revenue metrics")
        channel_revenue = df.groupby('channelGrouping')['totals.transactionRevenue'].agg(['sum', 'mean'])
        logger.info(f"Analyzed revenue for {len(channel_revenue)} channels")
        logger.debug(f"Top revenue channel: {channel_revenue.index[channel_revenue['sum'].argmax()]}")

        # Analyze source/medium combinations
        logger.debug("Analyzing source/medium combinations")
        source_medium = df.groupby(['trafficSource.source', 'trafficSource.medium'])[
            'totals.transactionRevenue'
        ].sum().reset_index().sort_values('totals.transactionRevenue', ascending=False).head(10)
        logger.info(f"Identified top {len(source_medium)} source/medium combinations")
        logger.debug(f"Top source/medium: {source_medium.iloc[0]['trafficSource.source']}/{source_medium.iloc[0]['trafficSource.medium']}")

        # Analyze campaign performance
        logger.debug("Calculating campaign performance metrics")
        campaign_performance = df.groupby('trafficSource.campaign').agg({
            'totals.transactionRevenue': ['sum', 'mean'],
            'totals.pageviews': 'mean',
            'totals.bounces': 'mean'
        }).reset_index()
        
        campaign_performance = campaign_performance.sort_values(
            ('totals.transactionRevenue', 'sum'), 
            ascending=False
        ).head(10)
        
        logger.info(f"Analyzed performance for top {len(campaign_performance)} campaigns")
        logger.debug(f"Top performing campaign: {campaign_performance.iloc[0]['trafficSource.campaign']}")

        metrics = {
            'channel_revenue': channel_revenue,
            'source_medium': source_medium,
            'campaign_performance': campaign_performance
        }

        execution_time = time.time() - start_time
        logger.info(f"Traffic source analysis completed in {execution_time:.2f} seconds")
        return metrics

    except Exception as e:
        logger.error("Error in traffic source analysis", exc_info=True)
        raise

def show_traffic_analytics(df):
    """Display traffic source analytics."""
    try:
        start_time = time.time()
        logger.info("Starting traffic analytics visualization")

        st.header("🔄 Traffic Source Analytics")
        
        # Get traffic statistics
        logger.debug("Retrieving traffic statistics")
        try:
            traffic_stats = analyze_traffic_sources(df)
        except Exception as e:
            logger.error("Error retrieving traffic statistics", exc_info=True)
            st.error("Error analyzing traffic sources")
            return

        col1, col2 = st.columns(2)
        
        with col1:
            try:
                logger.debug("Creating revenue by channel visualization")
                st.subheader("Revenue by Channel")
                fig = px.bar(
                    x=traffic_stats['channel_revenue'].index,
                    y=traffic_stats['channel_revenue']['sum'],
                    title="Total Revenue by Channel"
                )
                st.plotly_chart(fig)
                logger.info("Channel revenue chart displayed successfully")
            except Exception as e:
                logger.error("Error creating channel revenue chart", exc_info=True)
                st.error("Error displaying channel revenue")
        
        with col2:
            try:
                logger.debug("Creating source/medium visualization")
                st.subheader("Top Source/Medium Combinations")
                fig = px.bar(
                    traffic_stats['source_medium'],
                    x='trafficSource.source',
                    y='totals.transactionRevenue',
                    title="Revenue by Source/Medium"
                )
                st.plotly_chart(fig)
                logger.info("Source/medium chart displayed successfully")
            except Exception as e:
                logger.error("Error creating source/medium chart", exc_info=True)
                st.error("Error displaying source/medium combinations")
        
        # Display campaign performance
        try:
            logger.debug("Displaying campaign performance metrics")
            st.subheader("Campaign Performance")
            
            # Format campaign performance data for display
            formatted_performance = format_campaign_performance(
                traffic_stats['campaign_performance']
            )
            
            st.dataframe(formatted_performance)
            logger.info("Campaign performance table displayed successfully")
        except Exception as e:
            logger.error("Error displaying campaign performance", exc_info=True)
            st.error("Error displaying campaign performance metrics")

        execution_time = time.time() - start_time
        logger.info(f"Traffic analytics visualization completed in {execution_time:.2f} seconds")

    except Exception as e:
        logger.error("Error in traffic analytics visualization", exc_info=True)
        st.error("An error occurred while displaying traffic analytics")

def format_campaign_performance(performance_data):
    """Format campaign performance data for display."""
    try:
        logger.debug("Formatting campaign performance data")
        formatted = performance_data.copy()
        
        # Format revenue columns
        for col in formatted.columns:
            if 'Revenue' in str(col):
                formatted[col] = formatted[col].map('${:,.2f}'.format)
            elif 'mean' in str(col):
                formatted[col] = formatted[col].map('{:,.2f}'.format)
        
        logger.debug("Campaign performance data formatted successfully")
        return formatted
    except Exception as e:
        logger.error("Error formatting campaign performance data", exc_info=True)
        raise
