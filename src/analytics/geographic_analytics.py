"""Geographic insights analytics module."""
import plotly.express as px
import streamlit as st
import time
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

def show_geographic_insights(df):
    """Display geographic insights."""
    try:
        start_time = time.time()
        logger.info("Starting geographic insights analysis")
        logger.debug(f"Input dataframe shape: {df.shape}")

        st.header("🌍 Geographic Insights")
        
        # Continent and subcontinental analysis
        logger.info("Starting continent and subcontinental analysis")
        try:
            continent_metrics = analyze_continental_metrics(df)
            display_continental_visualization(continent_metrics)
        except Exception as e:
            logger.error("Error in continental analysis", exc_info=True)
            st.error("Error analyzing continental data")
        
        # Country analysis
        logger.info("Starting country-level analysis")
        try:
            country_revenue = analyze_country_revenue(df)
            display_country_visualizations(country_revenue)
        except Exception as e:
            logger.error("Error in country analysis", exc_info=True)
            st.error("Error analyzing country data")
        
        # City analysis
        logger.info("Starting city-level analysis")
        try:
            show_city_analysis(df)
        except Exception as e:
            logger.error("Error in city analysis", exc_info=True)
            st.error("Error analyzing city data")

        execution_time = time.time() - start_time
        logger.info(f"Geographic insights analysis completed in {execution_time:.2f} seconds")

    except Exception as e:
        logger.error("Error in geographic insights analysis", exc_info=True)
        st.error("An error occurred while analyzing geographic data")

def analyze_continental_metrics(df):
    """Analyze continental metrics."""
    try:
        logger.debug("Calculating continental metrics")
        continent_metrics = df.groupby(['geoNetwork.continent', 'geoNetwork.subContinent']).agg({
            'totals.transactionRevenue': ['sum', 'mean'],
            'totals.pageviews': 'mean',
            'totals.bounces': 'mean'
        })
        
        continent_metrics.columns = ['_'.join(col).strip() for col in continent_metrics.columns.values]
        continent_metrics = continent_metrics.reset_index()
        
        logger.info(f"Analyzed {len(continent_metrics)} continental regions")
        logger.debug(f"Continental metrics columns: {continent_metrics.columns.tolist()}")
        
        return continent_metrics
    except Exception as e:
        logger.error("Error calculating continental metrics", exc_info=True)
        raise

def display_continental_visualization(continent_metrics):
    """Display continental visualization."""
    try:
        logger.debug("Creating continental treemap visualization")
        st.subheader("Revenue by Continent")
        fig = px.treemap(
            continent_metrics,
            path=['geoNetwork.continent', 'geoNetwork.subContinent'],
            values='totals.transactionRevenue_sum',
            title="Revenue Distribution by Geographic Region"
        )
        st.plotly_chart(fig)
        logger.info("Continental treemap displayed successfully")
    except Exception as e:
        logger.error("Error creating continental visualization", exc_info=True)
        raise

def analyze_country_revenue(df):
    """Analyze country-level revenue."""
    try:
        logger.debug("Calculating country revenue metrics")
        country_revenue = df.groupby('geoNetwork.country')['totals.transactionRevenue'].agg([
            ('Total Revenue', 'sum'),
            ('Average Revenue', 'mean'),
            ('Number of Visits', 'count')
        ]).reset_index()
        
        country_revenue = country_revenue[
            country_revenue['geoNetwork.country'] != 'Unknown'
        ].sort_values('Total Revenue', ascending=False)
        
        logger.info(f"Analyzed revenue for {len(country_revenue)} countries")
        logger.debug(f"Top country by revenue: {country_revenue.iloc[0]['geoNetwork.country']}")
        
        return country_revenue
    except Exception as e:
        logger.error("Error calculating country revenue", exc_info=True)
        raise

def display_country_visualizations(country_revenue):
    """Display country-level visualizations."""
    try:
        logger.debug("Creating country choropleth visualization")
        st.subheader("Revenue by Country")
        fig = px.choropleth(
            country_revenue,
            locations='geoNetwork.country',
            locationmode='country names',
            color='Total Revenue',
            title='Revenue by Country',
            color_continuous_scale='Viridis'
        )
        fig.update_layout(height=600)
        st.plotly_chart(fig)
        logger.info("Country choropleth displayed successfully")
        
        # Show top countries table
        logger.debug("Formatting top countries data")
        st.subheader("Top Countries by Revenue")
        formatted_country_data = format_country_data(country_revenue.head(10))
        st.dataframe(formatted_country_data)
        logger.info("Top countries table displayed successfully")
        
    except Exception as e:
        logger.error("Error creating country visualizations", exc_info=True)
        raise

def format_country_data(data):
    """Format country data for display."""
    try:
        logger.debug("Formatting country data for display")
        formatted = data.copy()
        formatted['Total Revenue'] = formatted['Total Revenue'].map('${:,.2f}'.format)
        formatted['Average Revenue'] = formatted['Average Revenue'].map('${:,.2f}'.format)
        formatted['Number of Visits'] = formatted['Number of Visits'].map('{:,}'.format)
        
        logger.debug(f"Formatted data for {len(formatted)} countries")
        return formatted
    except Exception as e:
        logger.error("Error formatting country data", exc_info=True)
        raise

def show_city_analysis(df):
    """Show city-level analysis."""
    try:
        start_time = time.time()
        logger.info("Starting city-level analysis")
        
        st.subheader("Top Cities by Revenue")
        
        logger.debug("Calculating city revenue metrics")
        city_revenue = df.groupby(['geoNetwork.city', 'geoNetwork.country']).agg({
            'totals.transactionRevenue': ['sum', 'mean'],
            'totals.pageviews': 'mean'
        }).reset_index()
        
        city_revenue.columns = [
            'City', 'Country',
            'Total Revenue', 'Average Revenue',
            'Average Pageviews'
        ]
        
        # Filter and sort cities
        city_revenue = city_revenue[
            (city_revenue['City'] != 'Unknown') &
            (city_revenue['Country'] != 'Unknown')
        ].sort_values('Total Revenue', ascending=False).head(20)
        
        logger.info(f"Analyzed {len(city_revenue)} cities")
        logger.debug(f"Top city by revenue: {city_revenue.iloc[0]['City']}, {city_revenue.iloc[0]['Country']}")
        
        # Format metrics
        logger.debug("Formatting city metrics for display")
        city_revenue['Total Revenue'] = city_revenue['Total Revenue'].map('${:,.2f}'.format)
        city_revenue['Average Revenue'] = city_revenue['Average Revenue'].map('${:,.2f}'.format)
        city_revenue['Average Pageviews'] = city_revenue['Average Pageviews'].map('{:,.1f}'.format)
        
        st.dataframe(city_revenue)
        
        execution_time = time.time() - start_time
        logger.info(f"City analysis completed in {execution_time:.2f} seconds")
        
    except Exception as e:
        logger.error("Error in city analysis", exc_info=True)
        st.error("Error analyzing city data")
