# """Model training module for revenue prediction."""

# import numpy as np
# import pandas as pd
# import joblib
# import shap
# from lightgbm import LGBMRegressor
# from sklearn.model_selection import train_test_split
# from sklearn.metrics import mean_squared_error, r2_score
# from src.config import MODEL_PATH, FEATURE_IMPORTANCE_PATH, TOP_FEATURES_PATH, MODEL_PARAMS

# def train_model(X, y):
#     """Train and save the revenue prediction model."""
#     # Split data
#     X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
#     # Initialize and train model
#     model = LGBMRegressor(**MODEL_PARAMS)
#     model.fit(X_train, y_train)
    
#     # Calculate SHAP values
#     explainer = shap.TreeExplainer(model)
#     shap_values = explainer.shap_values(X_train)
    
#     # Calculate feature importance
#     importance = abs(shap_values).mean(axis=0)
#     feature_importance = pd.DataFrame({
#         'feature': X_train.columns,
#         'importance': importance
#     }).sort_values('importance', ascending=False)
    
#     # Save model artifacts
#     joblib.dump(model, MODEL_PATH)
#     joblib.dump(feature_importance, FEATURE_IMPORTANCE_PATH)
#     joblib.dump(feature_importance['feature'][:10].tolist(), TOP_FEATURES_PATH)
    
#     # Calculate metrics
#     y_pred = model.predict(X_test)
#     metrics = {
#         'rmse': np.sqrt(mean_squared_error(y_test, y_pred)),
#         'r2': r2_score(y_test, y_pred)
#     }
    
#     return {
#         'model': model,
#         'feature_importance': feature_importance,
#         'metrics': metrics
#     }













































import numpy as np
import pandas as pd
import joblib
import shap
from src.config import MODEL_PATH, FEATURE_IMPORTANCE_PATH, TOP_FEATURES_PATH, MODEL_PARAMS
from lightgbm import LGBMRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

def train_model(X, y):
    """Train and save the revenue prediction model."""
    try:
        logger.info("Starting model training process")
        
        # Split data
        logger.info("Splitting data into train and test sets")
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        # Initialize and train model
        logger.info("Initializing LightGBM model")
        model = LGBMRegressor(**MODEL_PARAMS)
        
        logger.info("Training model")
        model.fit(X_train, y_train)

        # Calculate SHAP values
        logger.info("Calculating SHAP values")
        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(X_train)

        # Calculate feature importance
        logger.info("Calculating feature importance")
        importance = abs(shap_values).mean(axis=0)
        feature_importance = pd.DataFrame({
            'feature': X_train.columns,
            'importance': importance
        }).sort_values('importance', ascending=False)

        # Save model artifacts
        logger.info("Saving model artifacts")
        joblib.dump(model, MODEL_PATH)
        joblib.dump(feature_importance, FEATURE_IMPORTANCE_PATH)
        joblib.dump(
            feature_importance['feature'][:10].tolist(), 
            TOP_FEATURES_PATH
        )

        # Calculate metrics
        logger.info("Calculating model metrics")
        y_pred = model.predict(X_test)
        metrics = {
            'rmse': np.sqrt(mean_squared_error(y_test, y_pred)),
            'r2': r2_score(y_test, y_pred)
        }
        
        logger.info(f"Model training completed. Metrics: {metrics}")
        return {
            'model': model,
            'feature_importance': feature_importance,
            'metrics': metrics
        }

    except Exception as e:
        logger.error(f"Error in model training: {str(e)}", exc_info=True)
        raise


