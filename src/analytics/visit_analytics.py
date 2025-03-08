# """Visit pattern analytics module."""

# import plotly.express as px
# import streamlit as st

# @st.cache_data
# def analyze_visit_patterns(df):
#     """Analyze visit timing and frequency patterns."""
#     return {
#         'hourly_visits': df.groupby('_visitHour').size(),
#         'weekday_revenue': df.groupby('_weekday')['totals.transactionRevenue'].mean(),
#         'visits_by_number': df.groupby('visitNumber').agg({
#             'totals.transactionRevenue': 'mean',
#             'totals.pageviews': 'mean'
#         })
#     }

# def show_visit_patterns(df):
#     """Display visit pattern analytics."""
#     st.header("⏰ Visit Pattern Analytics")
    
#     visit_stats = analyze_visit_patterns(df)
    
#     col1, col2 = st.columns(2)
    
#     with col1:
#         st.subheader("Hourly Visit Distribution")
#         fig = px.line(
#             x=visit_stats['hourly_visits'].index,
#             y=visit_stats['hourly_visits'].values,
#             title="Visits by Hour of Day"
#         )
#         st.plotly_chart(fig)
    
#     with col2:
#         st.subheader("Revenue by Day of Week")
#         fig = px.bar(
#             x=visit_stats['weekday_revenue'].index,
#             y=visit_stats['weekday_revenue'].values,
#             title="Average Revenue by Weekday"
#         )
#         st.plotly_chart(fig)
    
#     st.subheader("Visit Number Analysis")
#     fig = px.line(
#         visit_stats['visits_by_number'],
#         title="Metrics by Visit Number",
#         labels={'visitNumber': 'Visit Number'}
#     )
#     st.plotly_chart(fig)



















"""Visit pattern analytics module."""
import plotly.express as px
import streamlit as st
import time
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

@st.cache_data
def analyze_visit_patterns(df):
    """Analyze visit timing and frequency patterns."""
    try:
        start_time = time.time()
        logger.info("Starting visit pattern analysis")
        logger.debug(f"Input dataframe shape: {df.shape}")

        # Analyze hourly visits
        logger.debug("Calculating hourly visit patterns")
        hourly_visits = df.groupby('_visitHour').size()
        peak_hour = hourly_visits.idxmax()
        peak_visits = hourly_visits.max()
        logger.info(f"Peak visiting hour: {peak_hour}:00 with {peak_visits} visits")
        
        # Analyze weekday revenue
        logger.debug("Calculating weekday revenue patterns")
        weekday_revenue = df.groupby('_weekday')['totals.transactionRevenue'].mean()
        best_day = weekday_revenue.idxmax()
        max_revenue = weekday_revenue.max()
        logger.info(f"Highest revenue day: Day {best_day} with average revenue ${max_revenue:.2f}")
        
        # Analyze visits by number
        logger.debug("Analyzing visit number patterns")
        visits_by_number = df.groupby('visitNumber').agg({
            'totals.transactionRevenue': 'mean',
            'totals.pageviews': 'mean'
        })
        logger.info(f"Analyzed patterns for {len(visits_by_number)} visit numbers")
        
        metrics = {
            'hourly_visits': hourly_visits,
            'weekday_revenue': weekday_revenue,
            'visits_by_number': visits_by_number
        }

        execution_time = time.time() - start_time
        logger.info(f"Visit pattern analysis completed in {execution_time:.2f} seconds")
        
        # Log key statistics
        logger.debug(f"Hourly visits range: {hourly_visits.min()}-{hourly_visits.max()} visits")
        logger.debug(f"Weekday revenue range: ${weekday_revenue.min():.2f}-${weekday_revenue.max():.2f}")
        
        return metrics

    except Exception as e:
        logger.error("Error in visit pattern analysis", exc_info=True)
        raise

def show_visit_patterns(df):
    """Display visit pattern analytics."""
    try:
        start_time = time.time()
        logger.info("Starting visit pattern visualization")

        st.header("⏰ Visit Pattern Analytics")
        
        # Get visit statistics
        logger.debug("Retrieving visit pattern statistics")
        try:
            visit_stats = analyze_visit_patterns(df)
        except Exception as e:
            logger.error("Error retrieving visit statistics", exc_info=True)
            st.error("Error analyzing visit patterns")
            return

        col1, col2 = st.columns(2)
        
        with col1:
            try:
                logger.debug("Creating hourly visit distribution visualization")
                st.subheader("Hourly Visit Distribution")
                fig = px.line(
                    x=visit_stats['hourly_visits'].index,
                    y=visit_stats['hourly_visits'].values,
                    title="Visits by Hour of Day"
                )
                st.plotly_chart(fig)
                logger.info("Hourly visit distribution chart displayed successfully")
                
                # Log peak hours
                peak_hour = visit_stats['hourly_visits'].idxmax()
                logger.debug(f"Peak hour identified: {peak_hour}:00")
                
            except Exception as e:
                logger.error("Error creating hourly visit chart", exc_info=True)
                st.error("Error displaying hourly visit distribution")
        
        with col2:
            try:
                logger.debug("Creating weekday revenue visualization")
                st.subheader("Revenue by Day of Week")
                fig = px.bar(
                    x=visit_stats['weekday_revenue'].index,
                    y=visit_stats['weekday_revenue'].values,
                    title="Average Revenue by Weekday"
                )
                st.plotly_chart(fig)
                logger.info("Weekday revenue chart displayed successfully")
                
                # Log best performing day
                best_day = visit_stats['weekday_revenue'].idxmax()
                logger.debug(f"Best performing day identified: Day {best_day}")
                
            except Exception as e:
                logger.error("Error creating weekday revenue chart", exc_info=True)
                st.error("Error displaying weekday revenue")
        
        # Visit number analysis
        try:
            logger.debug("Creating visit number analysis visualization")
            st.subheader("Visit Number Analysis")
            fig = px.line(
                visit_stats['visits_by_number'],
                title="Metrics by Visit Number",
                labels={'visitNumber': 'Visit Number'}
            )
            st.plotly_chart(fig)
            logger.info("Visit number analysis chart displayed successfully")
            
            # Log visit number statistics
            max_visits = visit_stats['visits_by_number'].index.max()
            logger.debug(f"Maximum visit number analyzed: {max_visits}")
            
        except Exception as e:
            logger.error("Error creating visit number analysis chart", exc_info=True)
            st.error("Error displaying visit number analysis")

        execution_time = time.time() - start_time
        logger.info(f"Visit pattern visualization completed in {execution_time:.2f} seconds")

    except Exception as e:
        logger.error("Error in visit pattern visualization", exc_info=True)
        st.error("An error occurred while displaying visit patterns")

def format_visit_metrics(metrics):
    """Format visit metrics for display."""
    try:
        logger.debug("Formatting visit metrics")
        formatted = metrics.copy()
        
        # Format revenue values
        if 'totals.transactionRevenue' in formatted.columns:
            formatted['totals.transactionRevenue'] = formatted['totals.transactionRevenue'].map('${:,.2f}'.format)
        
        # Format pageview values
        if 'totals.pageviews' in formatted.columns:
            formatted['totals.pageviews'] = formatted['totals.pageviews'].map('{:,.1f}'.format)
        
        logger.debug("Visit metrics formatted successfully")
        return formatted
        
    except Exception as e:
        logger.error("Error formatting visit metrics", exc_info=True)
        raise