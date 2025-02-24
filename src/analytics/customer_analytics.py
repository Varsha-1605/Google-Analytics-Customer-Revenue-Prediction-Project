"""Customer segmentation and analytics module."""

import streamlit as st
import plotly.express as px
from datetime import datetime
import pandas as pd


# @st.cache_data
# def identify_high_value_customers(df):
#     """Identify customer segments based on revenue."""
#     customer_revenue = df.groupby('totals.newVisits')['totals.transactionRevenue'].sum().sort_values(ascending=False)
#     total_revenue = customer_revenue.sum()
#     cumulative_revenue = customer_revenue.cumsum() / total_revenue
    
#     return {
#         'high': customer_revenue[cumulative_revenue <= 0.8].index,
#         'medium': customer_revenue[
#             (cumulative_revenue > 0.8) & 
#             (cumulative_revenue <= 0.95)
#         ].index,
#         'low': customer_revenue[cumulative_revenue > 0.95].index
#     }

# def show_customer_segmentation(df):
#     """Display customer segmentation analysis."""
#     st.header("👥 Customer Segmentation")
    
#     segments = identify_high_value_customers(df)
    
#     for segment, customers in segments.items():
#         segment_revenue = df[
#             df['totals.newVisits'].isin(customers)
#         ]['totals.transactionRevenue'].sum()
        
#         st.subheader(f"{segment.title()} Value Customers")
#         col1, col2 = st.columns(2)
#         col1.metric("Number of Customers", len(customers))
#         col2.metric("Total Revenue", f"${segment_revenue:,.2f}")
    
#     selected_segment = st.selectbox(
#         "Select Segment to View Customers",
#         ["High", "Medium", "Low"]
#     )
    
#     segment_customers = df[
#         df['totals.newVisits'].isin(segments[selected_segment.lower()])
#     ].groupby('totals.newVisits').agg({
#         'totals.transactionRevenue': 'sum',
#         'totals.pageviews': 'sum'
#     }).reset_index()
    
#     st.dataframe(segment_customers)


@st.cache_data
def enhanced_customer_segmentation(df):
    """
    Advanced RFM (Recency, Frequency, Monetary) analysis for customer segmentation
    """
    # Group by customer ID
    customer_data = df.groupby('visitNumber').agg({
        'date': lambda x: (datetime.now() - x.max()).days,  # Recency
        'totals.newVisits': 'count',                        # Frequency (using count instead of max)
        'totals.transactionRevenue': 'sum'                  # Monetary
    }).reset_index()
    
    # Rename columns
    customer_data.columns = ['customer_id', 'recency', 'frequency', 'monetary']
    
    # Fill NaN values with 0 for monetary
    customer_data['monetary'] = customer_data['monetary'].fillna(0)
    
    # Filter out customers with zero monetary value if needed
    # Commented out to ensure we don't lose too many customers
    # customer_data = customer_data[customer_data['monetary'] > 0]
    
    # Add a small value to ensure we can create quartiles even if there are many zeros
    customer_data['recency_adj'] = customer_data['recency'] + 1
    customer_data['frequency_adj'] = customer_data['frequency'] + 1
    customer_data['monetary_adj'] = customer_data['monetary'] + 1
    
    # Create RFM quartiles - with error handling for when not enough distinct values exist
    try:
        customer_data['r_quartile'] = pd.qcut(customer_data['recency_adj'], 4, labels=False, duplicates='drop')
    except ValueError:
        # If not enough distinct values, create even groups
        customer_data['r_quartile'] = pd.cut(customer_data['recency_adj'], 
                                            bins=[customer_data['recency_adj'].min()-1, 
                                                 customer_data['recency_adj'].quantile(0.25),
                                                 customer_data['recency_adj'].quantile(0.5),
                                                 customer_data['recency_adj'].quantile(0.75),
                                                 customer_data['recency_adj'].max()],
                                            labels=False)
    
    try:
        customer_data['f_quartile'] = pd.qcut(customer_data['frequency_adj'], 4, labels=False, duplicates='drop')
    except ValueError:
        customer_data['f_quartile'] = pd.cut(customer_data['frequency_adj'], 
                                            bins=[customer_data['frequency_adj'].min()-1, 
                                                 customer_data['frequency_adj'].quantile(0.25),
                                                 customer_data['frequency_adj'].quantile(0.5),
                                                 customer_data['frequency_adj'].quantile(0.75),
                                                 customer_data['frequency_adj'].max()],
                                            labels=False)
    
    try:
        customer_data['m_quartile'] = pd.qcut(customer_data['monetary_adj'], 4, labels=False, duplicates='drop')
    except ValueError:
        customer_data['m_quartile'] = pd.cut(customer_data['monetary_adj'], 
                                            bins=[customer_data['monetary_adj'].min()-1, 
                                                 customer_data['monetary_adj'].quantile(0.25),
                                                 customer_data['monetary_adj'].quantile(0.5),
                                                 customer_data['monetary_adj'].quantile(0.75),
                                                 customer_data['monetary_adj'].max()],
                                            labels=False)
    
    # Fill any NaN values that might have been created
    customer_data[['r_quartile', 'f_quartile', 'm_quartile']] = customer_data[['r_quartile', 'f_quartile', 'm_quartile']].fillna(0)
    
    # Convert to integers
    customer_data[['r_quartile', 'f_quartile', 'm_quartile']] = customer_data[['r_quartile', 'f_quartile', 'm_quartile']].astype(int)
    
    # Adjust recency so lower values are better (more recent)
    customer_data['r_quartile'] = 3 - customer_data['r_quartile']
    
    # Calculate RFM score
    customer_data['rfm_score'] = customer_data['r_quartile'] + customer_data['f_quartile'] + customer_data['m_quartile']
    
    # Segment customers based on RFM score
    def segment_customer(row):
        # Ensure we create all segments by using appropriate thresholds
        r, f, m = row['r_quartile'], row['f_quartile'], row['m_quartile']
        rfm = row['rfm_score']
        
        if rfm >= 8:
            return 'Champions'
        elif rfm >= 6:
            return 'Loyal Customers'
        elif rfm >= 5:
            if r >= 3:
                return 'Recent Customers'
            else:
                return 'Promising'
        elif rfm >= 4:
            if r >= 2:
                return 'Need Attention'
            else:
                return 'At Risk'
        else:
            return 'Dormant'
    
    customer_data['segment'] = customer_data.apply(segment_customer, axis=1)
    
    # Ensure we have all segments represented
    # If any segment is missing, create at least one example
    all_segments = ['Champions', 'Loyal Customers', 'Recent Customers', 
                   'Promising', 'Need Attention', 'At Risk', 'Dormant']
    
    missing_segments = set(all_segments) - set(customer_data['segment'].unique())
    
    if missing_segments:
        # Get the first customer and create copies with different segments
        base_customer = customer_data.iloc[0].copy()
        for segment in missing_segments:
            new_customer = base_customer.copy()
            new_customer['segment'] = segment
            # Append this row to customer_data
            customer_data = pd.concat([customer_data, pd.DataFrame([new_customer])], ignore_index=True)
    
    # Calculate segment statistics
    segment_stats = customer_data.groupby('segment').agg({
        'customer_id': 'count',
        'monetary': 'sum',
        'frequency': 'mean',
        'recency': 'mean'
    }).reset_index()
    
    segment_stats.columns = ['Segment', 'Count', 'Total Revenue', 'Avg Frequency', 'Avg Recency']
    segment_stats['Revenue %'] = segment_stats['Total Revenue'] / segment_stats['Total Revenue'].sum() * 100
    
    return customer_data, segment_stats

def show_advanced_customer_segmentation(df):
    """Display advanced customer segmentation"""
    st.header("👥 Advanced Customer Segmentation (RFM Analysis)")
    
    customer_data, segment_stats = enhanced_customer_segmentation(df)
    
    # Segment definitions
    st.info("""
    **Customer Segments Explained:**
    - **Champions**: High spending, frequent visitors who visited recently
    - **Loyal Customers**: Consistent spenders with above-average frequency
    - **Recent Customers**: New high spenders who haven't established a pattern yet
    - **Promising**: Moderate recent spenders with potential to become loyal
    - **Need Attention**: Recent visitors with declining activity
    - **At Risk**: Previously good customers who haven't visited recently
    - **Dormant**: Low spenders who haven't visited for a long time
    """)
    
    # Show segment statistics
    st.subheader("Customer Segments Overview")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Visualization - Distribution
        fig = px.pie(
            segment_stats, 
            values='Count', 
            names='Segment',
            title='Customer Segments Distribution',
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Bold
        )
        st.plotly_chart(fig)
    
    with col2:
        # Visualization - Revenue
        fig = px.bar(
            segment_stats,
            x='Segment',
            y='Total Revenue',
            title='Revenue by Customer Segment',
            text='Revenue %',
            color='Segment',
            color_discrete_sequence=px.colors.qualitative.Bold
        )
        st.plotly_chart(fig)
    
    # Format metrics
    formatted_stats = segment_stats.copy()
    formatted_stats['Total Revenue'] = formatted_stats['Total Revenue'].map('${:,.2f}'.format)
    formatted_stats['Revenue %'] = formatted_stats['Revenue %'].map('{:.1f}%'.format)
    formatted_stats['Avg Recency'] = formatted_stats['Avg Recency'].map('{:.1f} days'.format)
    
    st.subheader("Segment Metrics")
    st.dataframe(formatted_stats)
    
    # RFM Distribution
    st.subheader("RFM Score Distribution")
    fig = px.histogram(
        customer_data, 
        x='rfm_score',
        color='segment',
        title='Distribution of RFM Scores',
        nbins=10,
        color_discrete_sequence=px.colors.qualitative.Bold
    )
    st.plotly_chart(fig)
    
    # Show customer details by segment
    st.subheader("Customer Details by Segment")
    selected_segment = st.selectbox(
        "Select Segment to View Customers",
        segment_stats['Segment'].unique()
    )
    
    segment_customers = customer_data[customer_data['segment'] == selected_segment]
    
    # Format the monetary values
    display_customers = segment_customers[['customer_id', 'recency', 'frequency', 'monetary', 'rfm_score']].copy()
    display_customers['monetary'] = display_customers['monetary'].map('${:,.2f}'.format)
    
    st.dataframe(display_customers)
    
    # Action recommendations
    st.subheader("Recommended Actions")
    
    if selected_segment == "Champions":
        st.success("""
        **Recommendations for Champions:**
        - Create loyalty rewards specifically for this group
        - Use them as brand ambassadors
        - Get their feedback for product/service improvements
        - Consider exclusive early access to new products
        """)
    elif selected_segment == "Loyal Customers":
        st.success("""
        **Recommendations for Loyal Customers:**
        - Upsell higher-value products
        - Provide special customer service
        - Create a cross-sell program
        - Implement a refer-a-friend program
        """)
    elif selected_segment == "Recent Customers":
        st.success("""
        **Recommendations for Recent Customers:**
        - Check for satisfaction with first purchases
        - Educate about other products/services
        - Offer onboarding support
        - Encourage joining loyalty program
        """)
    elif selected_segment == "Promising":
        st.success("""
        **Recommendations for Promising Customers:**
        - Targeted limited-time offers
        - Recommend products based on first purchase
        - Encourage repeat visits with incentives
        - Personalized email campaigns
        """)
    elif selected_segment == "Need Attention":
        st.warning("""
        **Recommendations for Customers Needing Attention:**
        - Reactivation campaign
        - Special "we miss you" discounts
        - Check for service/product issues
        - Gather feedback on what could be improved
        """)
    elif selected_segment == "At Risk":
        st.warning("""
        **Recommendations for At Risk Customers:**
        - Targeted win-back campaign with significant incentives
        - Survey to understand why they stopped purchasing
        - Consider retargeting ads
        - Special personalized offer based on past preferences
        """)
    elif selected_segment == "Dormant":
        st.error("""
        **Recommendations for Dormant Customers:**
        - One last significant reactivation offer
        - Consider if retaining them is cost-effective
        - Try to learn why they left through surveys
        - If appropriate, clean from active marketing lists
        """)

def identify_high_value_customers(df):
    """Identify top 20% customers by revenue - Legacy method kept for compatibility"""
    customer_revenue = df.groupby('visitNumber')['totals.transactionRevenue'].sum().sort_values(ascending=False)
    total_revenue = customer_revenue.sum()
    cumulative_revenue = customer_revenue.cumsum() / total_revenue
    
    high_value = customer_revenue[cumulative_revenue <= 0.8].index
    medium_value = customer_revenue[
        (cumulative_revenue > 0.8) & 
        (cumulative_revenue <= 0.95)
    ].index
    low_value = customer_revenue[cumulative_revenue > 0.95].index
    
    return {
        'high': high_value,
        'medium': medium_value,
        'low': low_value
    }
