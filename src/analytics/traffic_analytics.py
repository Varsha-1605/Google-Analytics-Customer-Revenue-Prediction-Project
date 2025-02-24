"""Traffic source analytics module."""

import plotly.express as px
import streamlit as st

@st.cache_data
def analyze_traffic_sources(df):
    """Analyze traffic sources and campaign performance."""
    return {
        'channel_revenue': df.groupby('channelGrouping')['totals.transactionRevenue'].agg(['sum', 'mean']),
        'source_medium': df.groupby(['trafficSource.source', 'trafficSource.medium'])['totals.transactionRevenue'].sum().reset_index().sort_values('totals.transactionRevenue', ascending=False).head(10),
        'campaign_performance': df.groupby('trafficSource.campaign').agg({
            'totals.transactionRevenue': ['sum', 'mean'],
            'totals.pageviews': 'mean',
            'totals.bounces': 'mean'
        }).reset_index().sort_values(('totals.transactionRevenue', 'sum'), ascending=False).head(10)
    }

def show_traffic_analytics(df):
    """Display traffic source analytics."""
    st.header("🔄 Traffic Source Analytics")
    
    traffic_stats = analyze_traffic_sources(df)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Revenue by Channel")
        fig = px.bar(
            x=traffic_stats['channel_revenue'].index,
            y=traffic_stats['channel_revenue']['sum'],
            title="Total Revenue by Channel"
        )
        st.plotly_chart(fig)
    
    with col2:
        st.subheader("Top Source/Medium Combinations")
        fig = px.bar(
            traffic_stats['source_medium'],
            x='trafficSource.source',
            y='totals.transactionRevenue',
            title="Revenue by Source/Medium"
        )
        st.plotly_chart(fig)
    
    st.subheader("Campaign Performance")
    st.dataframe(traffic_stats['campaign_performance'])