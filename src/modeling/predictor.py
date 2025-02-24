# """Revenue prediction module."""

# import numpy as np
# import pandas as pd
# import plotly.express as px
# import joblib
# import streamlit as st
# from src.config import MODEL_PATH, FEATURE_IMPORTANCE_PATH, TOP_FEATURES_PATH


# @st.cache_resource
# def load_trained_model():
#     """Load the trained model and artifacts."""
#     try:
#         model = joblib.load(MODEL_PATH)
#         feature_importance = joblib.load(FEATURE_IMPORTANCE_PATH)
#         return model, feature_importance
#     except Exception as e:
#         st.error(f"Error loading model: {str(e)}")
#         return None, None

# def show_prediction_interface():
#     """Display the prediction interface."""
#     st.header("💰 Revenue Prediction")
    
#     tab1, tab2 = st.tabs(["Train Model", "Make Predictions"])
    
#     with tab1:
#         show_training_tab()
    
#     with tab2:
#         show_prediction_tab()

# def show_training_tab():
#     """Display model training interface."""
#     if not st.session_state.get('model_trained', False) and st.button("Train New Model"):
#         with st.spinner("Training model..."):
#             # Model training code here
#             st.session_state.model_trained = True
            
#             col1, col2 = st.columns(2)
#             col1.metric("RMSE", f"{results['metrics']['rmse']:.4f}")
#             col2.metric("R² Score", f"{results['metrics']['r2']:.4f}")
            
#             show_feature_importance(results['feature_importance'])
#     elif st.session_state.get('model_trained', False):
#         st.success("Model has already been trained!")

# def show_prediction_tab():
#     """Display prediction making interface."""
#     model, feature_importance = load_trained_model()
    
#     if model is None:
#         st.warning("No trained model found. Please train a model first.")
#         return
    
#     st.subheader("Make Predictions")
#     top_features = joblib.load(TOP_FEATURES_PATH)
    
#     input_data = {}
#     for feature in top_features:
#         input_data[feature] = st.number_input(
#             f"Enter value for {feature}",
#             value=0.0
#         )
    
#     if st.button("Predict Revenue"):
#         prediction = make_prediction(model, input_data)
#         st.success(f"Predicted Revenue: ${prediction:,.2f}")

# def make_prediction(model, input_data):
#     """Make a revenue prediction."""
#     input_df = pd.DataFrame([input_data])
#     prediction = model.predict(input_df)
#     return np.expm1(prediction[0])

# def show_feature_importance(feature_importance):
#     """Display feature importance plot."""
#     st.subheader("Feature Importance")
#     fig = px.bar(
#         feature_importance.head(10),
#         x='importance',
#         y='feature',
#         orientation='h',
#         title='Top 10 Most Important Features'
#     )
#     st.plotly_chart(fig)



"""Revenue prediction module."""

import numpy as np
import pandas as pd
import plotly.express as px
import joblib
import streamlit as st
from src.config import MODEL_PATH, FEATURE_IMPORTANCE_PATH, TOP_FEATURES_PATH
from src.data_processor import process_data
from src.modeling.model_trainer import train_model

@st.cache_resource
def load_trained_model():
    """Load the trained model and artifacts."""
    try:
        model = joblib.load(MODEL_PATH)
        feature_importance = joblib.load(FEATURE_IMPORTANCE_PATH)
        return model, feature_importance
    except Exception as e:
        st.error(f"Error loading model: {str(e)}")
        return None, None

def show_prediction_interface(df):
    """Display the prediction interface."""
    st.header("💰 Revenue Prediction")
    
    tab1, tab2 = st.tabs(["Train Model", "Make Predictions"])
    
    with tab1:
        show_training_tab(df)
    
    with tab2:
        show_prediction_tab()

def show_training_tab(df):
    """Display model training interface."""
    if not st.session_state.get('model_trained', False) and st.button("Train New Model"):
        with st.spinner("Training model..."):
            # Process data
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
    elif st.session_state.get('model_trained', False):
        st.success("Model has already been trained!")

def show_prediction_tab():
    """Display prediction making interface."""
    model, feature_importance = load_trained_model()
    
    if model is None:
        st.warning("No trained model found. Please train a model first.")
        return
    
    st.subheader("Make Predictions")
    try:
        top_features = joblib.load(TOP_FEATURES_PATH)
        
        input_data = {}
        for feature in top_features:
            input_data[feature] = st.number_input(
                f"Enter value for {feature}",
                value=0.0
            )
        
        if st.button("Predict Revenue"):
            prediction = make_prediction(model, input_data)
            st.success(f"Predicted Revenue: ${prediction:,.2f}")
    except Exception as e:
        st.error(f"Error loading features: {str(e)}")

def make_prediction(model, input_data):
    """Make a revenue prediction."""
    input_df = pd.DataFrame([input_data])
    prediction = model.predict(input_df)
    return np.expm1(prediction[0])

def show_feature_importance(feature_importance):
    """Display feature importance plot."""
    st.subheader("Feature Importance")
    fig = px.bar(
        feature_importance.head(10),
        x='importance',
        y='feature',
        orientation='h',
        title='Top 10 Most Important Features'
    )
    st.plotly_chart(fig)