"""Geographic insights analytics module."""

import plotly.express as px
import streamlit as st

def show_geographic_insights(df):
    """Display geographic insights."""
    st.header("🌍 Geographic Insights")
    
    # Continent and subcontinental analysis
    continent_metrics = df.groupby(['geoNetwork.continent', 'geoNetwork.subContinent']).agg({
        'totals.transactionRevenue': ['sum', 'mean'],
        'totals.pageviews': 'mean',
        'totals.bounces': 'mean'
    })
    
    continent_metrics.columns = ['_'.join(col).strip() for col in continent_metrics.columns.values]
    continent_metrics = continent_metrics.reset_index()
    
    st.subheader("Revenue by Continent")
    fig = px.treemap(
        continent_metrics,
        path=['geoNetwork.continent', 'geoNetwork.subContinent'],
        values='totals.transactionRevenue_sum',
        title="Revenue Distribution by Geographic Region"
    )
    st.plotly_chart(fig)
    
    # Country analysis
    country_revenue = df.groupby('geoNetwork.country')['totals.transactionRevenue'].agg([
        ('Total Revenue', 'sum'),
        ('Average Revenue', 'mean'),
        ('Number of Visits', 'count')
    ]).reset_index()
    
    country_revenue = country_revenue[
        country_revenue['geoNetwork.country'] != 'Unknown'
    ].sort_values('Total Revenue', ascending=False)
    
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
    
    # Show top countries table
    st.subheader("Top Countries by Revenue")
    formatted_country_data = format_country_data(country_revenue.head(10))
    st.dataframe(formatted_country_data)
    
    # City analysis
    show_city_analysis(df)

def format_country_data(data):
    """Format country data for display."""
    formatted = data.copy()
    formatted['Total Revenue'] = formatted['Total Revenue'].map('${:,.2f}'.format)
    formatted['Average Revenue'] = formatted['Average Revenue'].map('${:,.2f}'.format)
    formatted['Number of Visits'] = formatted['Number of Visits'].map('{:,}'.format)
    return formatted

def show_city_analysis(df):
    """Show city-level analysis."""
    st.subheader("Top Cities by Revenue")
    
    city_revenue = df.groupby(['geoNetwork.city', 'geoNetwork.country']).agg({
        'totals.transactionRevenue': ['sum', 'mean'],
        'totals.pageviews': 'mean'
    }).reset_index()
    
    city_revenue.columns = [
        'City', 'Country',
        'Total Revenue', 'Average Revenue',
        'Average Pageviews'
    ]
    
    city_revenue = city_revenue[
        (city_revenue['City'] != 'Unknown') &
        (city_revenue['Country'] != 'Unknown')
    ].sort_values('Total Revenue', ascending=False).head(20)
    
    city_revenue['Total Revenue'] = city_revenue['Total Revenue'].map('${:,.2f}'.format)
    city_revenue['Average Revenue'] = city_revenue['Average Revenue'].map('${:,.2f}'.format)
    city_revenue['Average Pageviews'] = city_revenue['Average Pageviews'].map('{:,.1f}'.format)
    
    st.dataframe(city_revenue)