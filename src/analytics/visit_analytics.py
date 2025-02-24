"""Visit pattern analytics module."""

import plotly.express as px
import streamlit as st

@st.cache_data
def analyze_visit_patterns(df):
    """Analyze visit timing and frequency patterns."""
    return {
        'hourly_visits': df.groupby('_visitHour').size(),
        'weekday_revenue': df.groupby('_weekday')['totals.transactionRevenue'].mean(),
        'visits_by_number': df.groupby('visitNumber').agg({
            'totals.transactionRevenue': 'mean',
            'totals.pageviews': 'mean'
        })
    }

def show_visit_patterns(df):
    """Display visit pattern analytics."""
    st.header("⏰ Visit Pattern Analytics")
    
    visit_stats = analyze_visit_patterns(df)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Hourly Visit Distribution")
        fig = px.line(
            x=visit_stats['hourly_visits'].index,
            y=visit_stats['hourly_visits'].values,
            title="Visits by Hour of Day"
        )
        st.plotly_chart(fig)
    
    with col2:
        st.subheader("Revenue by Day of Week")
        fig = px.bar(
            x=visit_stats['weekday_revenue'].index,
            y=visit_stats['weekday_revenue'].values,
            title="Average Revenue by Weekday"
        )
        st.plotly_chart(fig)
    
    st.subheader("Visit Number Analysis")
    fig = px.line(
        visit_stats['visits_by_number'],
        title="Metrics by Visit Number",
        labels={'visitNumber': 'Visit Number'}
    )
    st.plotly_chart(fig)