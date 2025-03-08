"""Revenue prediction module."""
import numpy as np
import pandas as pd
import plotly.express as px
import joblib
import streamlit as st
import time
from src.config import MODEL_PATH, FEATURE_IMPORTANCE_PATH, TOP_FEATURES_PATH
from src.data_processor import process_data
from src.modeling.model_trainer import train_model
from src.utils.logger import setup_logger
from src.utils.latency_tracker import measure_latency, measure_batch_latency, latency_tracker

logger = setup_logger(__name__)

@measure_latency
def load_trained_model():
    """Load the trained model and artifacts."""
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
    """Make a revenue prediction."""
    try:
        start_time = time.time()
        input_df = pd.DataFrame([input_data])
        
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
    """Make predictions for a batch of data."""
    try:
        logger.debug(f"Making batch predictions with shape: {batch_data.shape}")
        
        # Ensure we're using the correct features
        top_features = joblib.load(TOP_FEATURES_PATH)
        # top_features = joblib.load(FEATURE_IMPORTANCE_PATH)
        if not all(feature in batch_data.columns for feature in top_features):
            logger.error("Missing required features in batch data")
            raise ValueError("Batch data missing required features")
            
        # Select only the features used in training
        batch_data = batch_data[top_features]
        
        predictions = model.predict(batch_data, predict_disable_shape_check=True)
        return np.expm1(predictions)
        
    except Exception as e:
        logger.error("Error in batch prediction", exc_info=True)
        raise


def show_latency_metrics():
    """Display model latency metrics."""
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
        
        # Create latency distribution plot
        if len(latency_tracker.response_times) > 1:
            fig = px.histogram(
                x=[t * 1000 for t in latency_tracker.response_times],
                title="Prediction Latency Distribution",
                labels={'x': 'Latency (ms)', 'y': 'Count'},
                nbins=20
            )
            st.plotly_chart(fig)

def show_prediction_interface(df):
    """Display the prediction interface."""
    st.header("💰 Revenue Prediction")
    
    tab1, tab2, tab3 = st.tabs(["Train Model", "Make Predictions", "Latency Metrics"])
    
    with tab1:
        show_training_tab(df)
    
    with tab2:
        show_prediction_tab()
        
    with tab3:
        show_latency_metrics()


def test_model_latency(model, test_data, batch_sizes=[1, 10, 100, 1000]):
    """Test model latency with different batch sizes."""
    try:
        logger.info("Starting model latency testing")
        logger.debug(f"Initial test data shape: {test_data.shape}")
        
        # Load the top features used in training
        top_features = joblib.load(TOP_FEATURES_PATH)
        logger.info(f"Loaded {len(top_features)} features for testing")
        
        # Ensure we only use the features the model was trained on
        test_data = test_data[top_features]
        logger.debug(f"Processed test data shape: {test_data.shape}")
        
        latency_results = []
        
        for batch_size in batch_sizes:
            if len(test_data) >= batch_size:
                logger.debug(f"Testing batch size: {batch_size}")
                batch = test_data.head(batch_size)
                
                # Warm-up run
                _ = make_batch_predictions(model, batch)
                
                # Actual timing
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
                           f"({(execution_time*1000)/batch_size:.2f}ms per record)")
        
        return pd.DataFrame(latency_results)
        
    except Exception as e:
        logger.error("Error in latency testing", exc_info=True)
        raise


def show_training_tab(df):
    """Display model training interface."""
    if not st.session_state.get('model_trained', False) and st.button("Train New Model"):
        with st.spinner("Training model..."):
            try:
                # Process data
                logger.info("Processing data for training")
                processed_df = process_data(df)
                X = processed_df.drop(['totals.transactionRevenue', 'date'], axis=1)
                y = processed_df['totals.transactionRevenue'].fillna(0)
                y = np.log1p(y)  # Log transform the target variable
                
                # Train model and get results
                results = train_model(X, y)
                st.session_state.model_trained = True
                
                # Display metrics
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
                    # Process data
                    processed_df = process_data(df)
                    X = processed_df.drop(['totals.transactionRevenue', 'date'], axis=1)
                    
                    # Run latency tests
                    results = test_model_latency(model, X)
                    
                    # Display results
                    st.subheader("Latency Test Results")
                    
                    # Format results for display
                    display_results = results.copy()
                    display_results['latency_ms'] = display_results['latency_ms'].round(2)
                    display_results['latency_per_record_ms'] = display_results['latency_per_record_ms'].round(2)
                    st.dataframe(display_results)
                    
                    # Create visualization
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
                    st.warning("Please train a model first")
                    
            except Exception as e:
                logger.error("Error in latency testing", exc_info=True)
                st.error(f"Error during latency testing: {str(e)}")
    
    elif st.session_state.get('model_trained', False):
        st.success("Model has already been trained!")

def show_prediction_tab():
    """Display prediction making interface."""
    try:
        logger.info("Initializing prediction tab")
        model, feature_importance = load_trained_model()
        
        if model is None:
            logger.warning("No trained model found")
            st.warning("No trained model found. Please train a model first.")
            return
        
        st.subheader("Make Predictions")
        
        try:
            logger.debug("Loading top features")
            top_features = joblib.load(TOP_FEATURES_PATH)
            logger.info(f"Loaded {len(top_features)} top features")
            
            input_data = {}
            for feature in top_features:
                input_data[feature] = st.number_input(
                    f"Enter value for {feature}",
                    value=0.0
                )
            
            if st.button("Predict Revenue"):
                logger.info("Making new prediction")
                prediction = make_prediction(model, input_data)
                logger.info(f"Prediction made: ${prediction:,.2f}")
                st.success(f"Predicted Revenue: ${prediction:,.2f}")
                
        except Exception as e:
            logger.error(f"Error loading features: {str(e)}", exc_info=True)
            st.error(f"Error loading features: {str(e)}")
            
    except Exception as e:
        logger.error("Error in prediction tab", exc_info=True)
        st.error("Error initializing prediction interface")


def show_feature_importance(feature_importance):
    """Display feature importance plot."""
    try:
        logger.info("Creating feature importance visualization")
        st.subheader("Feature Importance")
        
        fig = px.bar(
            feature_importance.head(10),
            x='importance',
            y='feature',
            orientation='h',
            title='Top 10 Most Important Features'
        )
        
        st.plotly_chart(fig)
        logger.info("Feature importance visualization displayed successfully")
        
        # Log top features
        top_features = feature_importance.head(3)['feature'].tolist()
        logger.debug(f"Top 3 most important features: {top_features}")
        
    except Exception as e:
        logger.error("Error displaying feature importance", exc_info=True)
        st.error("Error displaying feature importance plot")










