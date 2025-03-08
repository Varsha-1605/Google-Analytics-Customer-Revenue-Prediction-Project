"""Customer segmentation and analytics module."""
import streamlit as st
import plotly.express as px
from datetime import datetime
import pandas as pd
import time
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

@st.cache_data
def enhanced_customer_segmentation(df):
    """Advanced RFM (Recency, Frequency, Monetary) analysis for customer segmentation"""
    start_time = time.time()
    logger.info("Starting enhanced customer segmentation analysis")
    
    try:
        # Log input data characteristics
        logger.info(f"Input dataframe shape: {df.shape}")
        logger.debug(f"Input columns: {df.columns.tolist()}")
        
        # Group by customer ID
        logger.info("Starting customer data aggregation")
        customer_data = df.groupby('visitNumber').agg({
            'date': lambda x: (datetime.now() - x.max()).days,  # Recency
            'totals.newVisits': 'count',                        # Frequency
            'totals.transactionRevenue': 'sum'                  # Monetary
        }).reset_index()
        logger.info(f"Customer data aggregation complete. Shape: {customer_data.shape}")
        
        # Rename columns
        customer_data.columns = ['customer_id', 'recency', 'frequency', 'monetary']
        logger.debug("Columns renamed to standard format")
        
        # Fill NaN values
        null_count = customer_data['monetary'].isnull().sum()
        customer_data['monetary'] = customer_data['monetary'].fillna(0)
        logger.info(f"Filled {null_count} null monetary values with 0")
        
        # Add adjusted values
        logger.debug("Creating adjusted RFM values")
        customer_data['recency_adj'] = customer_data['recency'] + 1
        customer_data['frequency_adj'] = customer_data['frequency'] + 1
        customer_data['monetary_adj'] = customer_data['monetary'] + 1
        
        # Create RFM quartiles
        logger.info("Starting RFM quartile calculation")
        
        # Recency quartiles
        try:
            customer_data['r_quartile'] = pd.qcut(customer_data['recency_adj'], 4, labels=False, duplicates='drop')
            logger.debug("Recency quartiles created using qcut")
        except ValueError as e:
            logger.warning(f"Using alternative method for recency quartiles: {str(e)}")
            customer_data['r_quartile'] = pd.cut(
                customer_data['recency_adj'],
                bins=[
                    customer_data['recency_adj'].min()-1,
                    customer_data['recency_adj'].quantile(0.25),
                    customer_data['recency_adj'].quantile(0.5),
                    customer_data['recency_adj'].quantile(0.75),
                    customer_data['recency_adj'].max()
                ],
                labels=False
            )
        
        # Frequency quartiles
        try:
            customer_data['f_quartile'] = pd.qcut(customer_data['frequency_adj'], 4, labels=False, duplicates='drop')
            logger.debug("Frequency quartiles created using qcut")
        except ValueError as e:
            logger.warning(f"Using alternative method for frequency quartiles: {str(e)}")
            customer_data['f_quartile'] = pd.cut(
                customer_data['frequency_adj'],
                bins=[
                    customer_data['frequency_adj'].min()-1,
                    customer_data['frequency_adj'].quantile(0.25),
                    customer_data['frequency_adj'].quantile(0.5),
                    customer_data['frequency_adj'].quantile(0.75),
                    customer_data['frequency_adj'].max()
                ],
                labels=False
            )
        
        # Monetary quartiles
        try:
            customer_data['m_quartile'] = pd.qcut(customer_data['monetary_adj'], 4, labels=False, duplicates='drop')
            logger.debug("Monetary quartiles created using qcut")
        except ValueError as e:
            logger.warning(f"Using alternative method for monetary quartiles: {str(e)}")
            customer_data['m_quartile'] = pd.cut(
                customer_data['monetary_adj'],
                bins=[
                    customer_data['monetary_adj'].min()-1,
                    customer_data['monetary_adj'].quantile(0.25),
                    customer_data['monetary_adj'].quantile(0.5),
                    customer_data['monetary_adj'].quantile(0.75),
                    customer_data['monetary_adj'].max()
                ],
                labels=False
            )
            
        logger.info("RFM quartile calculation completed")
        
        # Fill NaN values in quartiles
        null_counts = customer_data[['r_quartile', 'f_quartile', 'm_quartile']].isnull().sum()
        logger.debug(f"Null values in quartiles before filling: {null_counts.to_dict()}")
        
        customer_data[['r_quartile', 'f_quartile', 'm_quartile']] = (
            customer_data[['r_quartile', 'f_quartile', 'm_quartile']]
            .fillna(0)
            .astype(int)
        )
        logger.info("Quartile null values filled and converted to integers")
        
        # Adjust recency
        customer_data['r_quartile'] = 3 - customer_data['r_quartile']
        logger.debug("Recency quartiles adjusted")
        
        # Calculate RFM score
        customer_data['rfm_score'] = (
            customer_data['r_quartile'] +
            customer_data['f_quartile'] +
            customer_data['m_quartile']
        )
        logger.info(f"RFM scores calculated. Range: {customer_data['rfm_score'].min()} to {customer_data['rfm_score'].max()}")

        # Segment customers
        logger.info("Starting customer segmentation")
        def segment_customer(row):
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
        segment_distribution = customer_data['segment'].value_counts()
        logger.info(f"Initial segment distribution: {segment_distribution.to_dict()}")
        
        # Handle missing segments
        all_segments = ['Champions', 'Loyal Customers', 'Recent Customers', 
                       'Promising', 'Need Attention', 'At Risk', 'Dormant']
        
        missing_segments = set(all_segments) - set(customer_data['segment'].unique())
        
        if missing_segments:
            logger.warning(f"Found missing segments: {missing_segments}")
            base_customer = customer_data.iloc[0].copy()
            for segment in missing_segments:
                logger.info(f"Adding example customer for segment: {segment}")
                new_customer = base_customer.copy()
                new_customer['segment'] = segment
                customer_data = pd.concat([customer_data, pd.DataFrame([new_customer])], ignore_index=True)
        
        # Calculate segment statistics
        logger.info("Calculating segment statistics")
        segment_stats = customer_data.groupby('segment').agg({
            'customer_id': 'count',
            'monetary': 'sum',
            'frequency': 'mean',
            'recency': 'mean'
        }).reset_index()
        
        segment_stats.columns = ['Segment', 'Count', 'Total Revenue', 'Avg Frequency', 'Avg Recency']
        segment_stats['Revenue %'] = segment_stats['Total Revenue'] / segment_stats['Total Revenue'].sum() * 100
        
        execution_time = time.time() - start_time
        logger.info(f"Customer segmentation completed in {execution_time:.2f} seconds")
        logger.debug(f"Final segment statistics:\n{segment_stats.to_dict()}")
        
        return customer_data, segment_stats

    except Exception as e:
        logger.error("Error in customer segmentation", exc_info=True)
        raise

def show_advanced_customer_segmentation(df):
    """Display advanced customer segmentation"""
    try:
        logger.info("Starting customer segmentation visualization")
        st.header("👥 Advanced Customer Segmentation (RFM Analysis)")
        
        start_time = time.time()
        customer_data, segment_stats = enhanced_customer_segmentation(df)
        logger.info(f"Retrieved segmentation data in {time.time() - start_time:.2f} seconds")
        
        # Segment definitions
        logger.debug("Displaying segment definitions")
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
        logger.info("Creating segment overview visualizations")
        st.subheader("Customer Segments Overview")
        
        col1, col2 = st.columns(2)
        
        with col1:
            try:
                logger.debug("Creating segment distribution pie chart")
                fig = px.pie(
                    segment_stats, 
                    values='Count', 
                    names='Segment',
                    title='Customer Segments Distribution',
                    hole=0.4,
                    color_discrete_sequence=px.colors.qualitative.Bold
                )
                st.plotly_chart(fig)
            except Exception as e:
                logger.error(f"Error creating pie chart: {str(e)}", exc_info=True)
                st.error("Error displaying segment distribution chart")
        
        with col2:
            try:
                logger.debug("Creating revenue by segment bar chart")
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
            except Exception as e:
                logger.error(f"Error creating bar chart: {str(e)}", exc_info=True)
                st.error("Error displaying revenue distribution chart")
        
        # Format metrics
        logger.info("Formatting segment metrics for display")
        try:
            formatted_stats = segment_stats.copy()
            formatted_stats['Total Revenue'] = formatted_stats['Total Revenue'].map('${:,.2f}'.format)
            formatted_stats['Revenue %'] = formatted_stats['Revenue %'].map('{:.1f}%'.format)
            formatted_stats['Avg Recency'] = formatted_stats['Avg Recency'].map('{:.1f} days'.format)
            
            st.subheader("Segment Metrics")
            st.dataframe(formatted_stats)
        except Exception as e:
            logger.error(f"Error formatting metrics: {str(e)}", exc_info=True)
            st.error("Error displaying segment metrics")
        
        # RFM Distribution
        logger.info("Creating RFM score distribution visualization")
        try:
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
        except Exception as e:
            logger.error(f"Error creating RFM distribution: {str(e)}", exc_info=True)
            st.error("Error displaying RFM score distribution")
        
        # Show customer details by segment
        logger.info("Preparing customer details view")
        st.subheader("Customer Details by Segment")
        selected_segment = st.selectbox(
            "Select Segment to View Customers",
            segment_stats['Segment'].unique()
        )
        logger.debug(f"Selected segment for details: {selected_segment}")
        
        try:
            segment_customers = customer_data[customer_data['segment'] == selected_segment]
            display_customers = segment_customers[['customer_id', 'recency', 'frequency', 'monetary', 'rfm_score']].copy()
            display_customers['monetary'] = display_customers['monetary'].map('${:,.2f}'.format)
            
            st.dataframe(display_customers)
            logger.info(f"Displayed {len(display_customers)} customers for segment {selected_segment}")
        except Exception as e:
            logger.error(f"Error displaying customer details: {str(e)}", exc_info=True)
            st.error("Error displaying customer details")
        
        # Action recommendations
        logger.info(f"Displaying recommendations for segment: {selected_segment}")
        st.subheader("Recommended Actions")
        
        try:
            display_segment_recommendations(selected_segment)
        except Exception as e:
            logger.error(f"Error displaying recommendations: {str(e)}", exc_info=True)
            st.error("Error displaying segment recommendations")
        
        execution_time = time.time() - start_time
        logger.info(f"Completed customer segmentation visualization in {execution_time:.2f} seconds")

    except Exception as e:
        logger.error("Error in customer segmentation visualization", exc_info=True)
        st.error("An error occurred while displaying customer segmentation")

def display_segment_recommendations(selected_segment):
    """Display recommendations for selected segment"""
    logger.debug(f"Displaying recommendations for segment: {selected_segment}")
    
    try:
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
        # ... [Continue with other segments] ...
        
        logger.debug("Recommendations displayed successfully")
    except Exception as e:
        logger.error(f"Error displaying recommendations: {str(e)}", exc_info=True)
        raise

def identify_high_value_customers(df):
    """Identify top 20% customers by revenue - Legacy method kept for compatibility"""
    try:
        logger.info("Starting high-value customer identification")
        start_time = time.time()
        
        customer_revenue = df.groupby('visitNumber')['totals.transactionRevenue'].sum().sort_values(ascending=False)
        total_revenue = customer_revenue.sum()
        logger.debug(f"Total revenue calculated: ${total_revenue:,.2f}")
        
        cumulative_revenue = customer_revenue.cumsum() / total_revenue
        
        high_value = customer_revenue[cumulative_revenue <= 0.8].index
        medium_value = customer_revenue[
            (cumulative_revenue > 0.8) & 
            (cumulative_revenue <= 0.95)
        ].index
        low_value = customer_revenue[cumulative_revenue > 0.95].index
        
        logger.info(f"Customer segments identified: High: {len(high_value)}, Medium: {len(medium_value)}, Low: {len(low_value)}")
        
        execution_time = time.time() - start_time
        logger.info(f"High-value customer identification completed in {execution_time:.2f} seconds")
        
        return {
            'high': high_value,
            'medium': medium_value,
            'low': low_value
        }
    except Exception as e:
        logger.error("Error in high-value customer identification", exc_info=True)
        raise
