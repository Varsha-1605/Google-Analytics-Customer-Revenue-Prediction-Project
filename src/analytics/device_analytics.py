"""Device and browser analytics module."""

import plotly.express as px
import streamlit as st

@st.cache_data
def analyze_device_metrics(df):
    """Analyze device and browser related metrics."""
    return {
        'browser_usage': df['device.browser'].value_counts().head(10),
        'os_usage': df['device.operatingSystem'].value_counts().head(10),
        'device_category': df['device.deviceCategory'].value_counts(),
        'mobile_usage': df['device.isMobile'].value_counts(),
        'avg_revenue_by_device': df.groupby('device.deviceCategory')['totals.transactionRevenue'].mean(),
        'avg_pageviews_by_device': df.groupby('device.deviceCategory')['totals.pageviews'].mean()
    }

def show_device_analytics(df):
    """Display device and browser analytics."""
    st.header("📱 Device & Browser Analytics")
    
    device_stats = analyze_device_metrics(df)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Device Category Distribution")
        fig = px.pie(
            values=device_stats['device_category'].values,
            names=device_stats['device_category'].index,
            title="Traffic by Device Category"
        )
        st.plotly_chart(fig)
        
        st.subheader("Operating System Usage")
        fig = px.bar(
            x=device_stats['os_usage'].index,
            y=device_stats['os_usage'].values,
            title="Top Operating Systems"
        )
        st.plotly_chart(fig)
    
    with col2:
        st.subheader("Average Revenue by Device")
        fig = px.bar(
            x=device_stats['avg_revenue_by_device'].index,
            y=device_stats['avg_revenue_by_device'].values,
            title="Average Revenue by Device Category"
        )
        st.plotly_chart(fig)
        
        st.subheader("Browser Usage")
        fig = px.bar(
            x=device_stats['browser_usage'].index,
            y=device_stats['browser_usage'].values,
            title="Top Browsers"
        )
        st.plotly_chart(fig)