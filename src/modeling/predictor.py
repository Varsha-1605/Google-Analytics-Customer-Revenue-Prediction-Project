

"""
Revenue prediction module.
Adjust ALL_TRAINING_FEATURES in show_prediction_tab() to match
the columns used when training your LightGBM model.
"""

import numpy as np
import pandas as pd
import plotly.express as px
import joblib
import streamlit as st
import time
from src.config import MODEL_PATH, FEATURE_IMPORTANCE_PATH
from src.data_processor import process_data
from src.modeling.model_trainer import train_model
from src.utils.logger import setup_logger
from src.utils.latency_tracker import measure_latency, measure_batch_latency, latency_tracker

logger = setup_logger(__name__)

@measure_latency
def load_trained_model():
    """Load the trained model and feature importance artifacts."""
    try:
        logger.info("Loading model artifacts")
        model = joblib.load(MODEL_PATH)
        feature_importance = joblib.load(FEATURE_IMPORTANCE_PATH)
        return model, feature_importance
    except Exception as e:
        logger.error(f"Error loading model: {str(e)}", exc_info=True)
        return None, None

@measure_latency
def make_prediction(model, input_data):
    """
    Make a single revenue prediction.
    Expects a dictionary of ALL training features as input_data.
    """
    try:
        start_time = time.time()
        input_df = pd.DataFrame([input_data])  # DataFrame with matching columns
        prediction = model.predict(input_df, predict_disable_shape_check=True)
        final_prediction = np.expm1(prediction[0])

        execution_time = time.time() - start_time
        logger.info(f"Prediction latency: {execution_time*1000:.2f}ms")

        return final_prediction
    except Exception as e:
        logger.error("Error making prediction", exc_info=True)
        raise

@measure_batch_latency
def make_batch_predictions(model, batch_data):
    """
    Make predictions for a batch of data.
    Expects a DataFrame with the full set of training features.
    """
    try:
        logger.debug(f"Making batch predictions with shape: {batch_data.shape}")
        predictions = model.predict(batch_data, predict_disable_shape_check=True)
        return np.expm1(predictions)
    except Exception as e:
        logger.error("Error in batch prediction", exc_info=True)
        raise

def test_model_latency(model, test_data, batch_sizes=[1, 10, 100, 1000]):
    """
    Test model latency on different batch sizes.
    Expects test_data to include ALL features the model was trained on.
    """
    try:
        logger.info("Starting model latency testing")
        latency_results = []

        # Warm-up run (optional)
        _ = make_batch_predictions(model, test_data.head(1))

        for batch_size in batch_sizes:
            if len(test_data) >= batch_size:
                batch = test_data.head(batch_size)
                start_time = time.time()
                _ = make_batch_predictions(model, batch)
                execution_time = time.time() - start_time

                result = {
                    'batch_size': batch_size,
                    'latency_ms': execution_time * 1000,
                    'latency_per_record_ms': (execution_time * 1000) / batch_size
                }
                latency_results.append(result)
                logger.info(f"Batch size {batch_size}: {execution_time*1000:.2f}ms "
                            f"({(execution_time*1000)/batch_size:.2f}ms/record)")

        return pd.DataFrame(latency_results)
    except Exception as e:
        logger.error("Error in latency testing", exc_info=True)
        raise

def show_latency_metrics():
    """Display latency statistics in Streamlit."""
    stats = latency_tracker.get_statistics()
    if stats:
        st.subheader("Model Latency Metrics")
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Average Response Time", f"{stats['avg_response_time']:.2f}ms")
            st.metric("Total Predictions", stats['total_predictions'])

        with col2:
            st.metric("Median Response Time", f"{stats['median_response_time']:.2f}ms")
            if 'total_batches' in stats:
                st.metric("Total Batch Predictions", stats['total_batches'])

        with col3:
            st.metric("Max Response Time", f"{stats['max_response_time']:.2f}ms")
            st.metric("Min Response Time", f"{stats['min_response_time']:.2f}ms")

        # Optional distribution plot
        if len(latency_tracker.response_times) > 1:
            fig = px.histogram(
                x=[t * 1000 for t in latency_tracker.response_times],
                title="Prediction Latency Distribution",
                labels={'x': 'Latency (ms)', 'y': 'Count'},
                nbins=20
            )
            st.plotly_chart(fig)

def show_prediction_interface(df):
    """Display the main interface with tabs for training, prediction, and latency."""
    st.header("💰 Revenue Prediction")
    tab1, tab2, tab3 = st.tabs(["Train Model", "Make Predictions", "Latency Metrics"])

    with tab1:
        show_training_tab(df)
    with tab2:
        show_prediction_tab()
    with tab3:
        show_latency_metrics()

def show_training_tab(df):
    """Handle model training and latency testing."""
    if not st.session_state.get('model_trained', False) and st.button("Train New Model"):
        with st.spinner("Training model..."):
            try:
                logger.info("Processing data for training")
                processed_df = process_data(df)
                X = processed_df.drop(['totals.transactionRevenue', 'date'], axis=1)
                y = processed_df['totals.transactionRevenue'].fillna(0)
                y = np.log1p(y)

                results = train_model(X, y)
                st.session_state.model_trained = True

                col1, col2 = st.columns(2)
                col1.metric("RMSE", f"{results['metrics']['rmse']:.4f}")
                col2.metric("R² Score", f"{results['metrics']['r2']:.4f}")

                show_feature_importance(results['feature_importance'])
            except Exception as e:
                logger.error("Error in model training", exc_info=True)
                st.error(f"Error during model training: {str(e)}")
    elif st.button("Test Model Latency"):
        with st.spinner("Testing model latency..."):
            try:
                model, _ = load_trained_model()
                if model:
                    processed_df = process_data(df)
                    X = processed_df.drop(['totals.transactionRevenue', 'date'], axis=1)

                    results = test_model_latency(model, X)
                    st.subheader("Latency Test Results")

                    display_results = results.copy()
                    display_results['latency_ms'] = display_results['latency_ms'].round(2)
                    display_results['latency_per_record_ms'] = display_results['latency_per_record_ms'].round(2)
                    st.dataframe(display_results)

                    fig = px.line(
                        results,
                        x='batch_size',
                        y=['latency_ms', 'latency_per_record_ms'],
                        title="Latency vs Batch Size",
                        labels={
                            'value': 'Latency (ms)',
                            'batch_size': 'Batch Size',
                            'variable': 'Metric'
                        }
                    )
                    st.plotly_chart(fig)
                else:
                    st.warning("No trained model found. Please train a model first.")
            except Exception as e:
                logger.error("Error in latency testing", exc_info=True)
                st.error(f"Error during latency testing: {str(e)}")
    elif st.session_state.get('model_trained', False):
        st.success("Model has already been trained!")

def show_prediction_tab():
    """Display interface to make single predictions."""
    try:
        model, feature_importance = load_trained_model()
        if model is None:
            st.warning("No trained model found. Please train a model first.")
            return

        st.subheader("Make Predictions")

        # (IMPORTANT) Replace this with the COMPLETE, EXACT list of features used at training:
        ALL_TRAINING_FEATURES = ['channelGrouping', 'visitNumber', 'visitStartTime', 'device.browser',
       'device.operatingSystem', 'device.deviceCategory',
       'geoNetwork.continent', 'geoNetwork.subContinent', 'geoNetwork.country',
       'geoNetwork.region', 'geoNetwork.metro', 'geoNetwork.city',
       'geoNetwork.networkDomain', 'totals.hits', 'totals.pageviews',
       'totals.bounces', 'totals.newVisits', 'totals.transactionRevenue',
       'trafficSource.campaign', 'trafficSource.source',
       'trafficSource.medium', 'trafficSource.keyword',
       'trafficSource.isTrueDirect', 'trafficSource.referralPath',
       'trafficSource.adwordsClickInfo.page',
       'trafficSource.adwordsClickInfo.slot',
       'trafficSource.adwordsClickInfo.gclId',
       'trafficSource.adwordsClickInfo.adNetworkType',
       'trafficSource.adwordsClickInfo.isVideoAd', 'trafficSource.adContent',
       '_weekday', '_day', '_month', '_year', '_visitHour']

        input_data = {}
        for feature in ALL_TRAINING_FEATURES:
            input_data[feature] = st.number_input(
                f"Enter value for {feature}",
                value=0.0
            )

        if st.button("Predict Revenue"):
            prediction = make_prediction(model, input_data)
            st.success(f"Predicted Revenue: ${prediction:,.2f}")

    except Exception as e:
        logger.error("Error in prediction tab", exc_info=True)
        st.error("Error initializing prediction interface")

def show_feature_importance(feature_importance):
    """Display a bar chart of top feature importances."""
    try:
        st.subheader("Feature Importance")
        fig = px.bar(
            feature_importance.head(10),
            x='importance',
            y='feature',
            orientation='h',
            title='Top 10 Most Important Features'
        )
        st.plotly_chart(fig)
    except Exception as e:
        logger.error("Error displaying feature importance", exc_info=True)
        st.error("Error displaying feature importance plot")


