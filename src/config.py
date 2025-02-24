# """Configuration settings for the Revenue Analytics Dashboard."""

# import os

# # Project paths
# PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# DATA_PATH = os.path.join(PROJECT_ROOT, "data", "new_file (1).csv")
# MODELS_DIR = os.path.join(PROJECT_ROOT, "models")

# # Model file paths
# MODEL_PATH = os.path.join(MODELS_DIR, "revenue_model.joblib")
# FEATURE_IMPORTANCE_PATH = os.path.join(MODELS_DIR, "feature_importance.joblib")
# TOP_FEATURES_PATH = os.path.join(MODELS_DIR, "top_features.joblib")

# # Page configuration
# PAGE_CONFIG = {
#     "page_title": "Revenue Analytics Dashboard",
#     "page_icon": "💰",
#     "layout": "wide"
# }

# # Analytics settings
# GEOGRAPHIC_COLUMNS = [
#     'geoNetwork.continent',
#     'geoNetwork.subContinent',
#     'geoNetwork.country',
#     'geoNetwork.region',
#     'geoNetwork.metro',
#     'geoNetwork.city'
# ]

# # Model parameters
# MODEL_PARAMS = {
#     'n_estimators': 200,
#     'learning_rate': 0.05,
#     'random_state': 42
# }

























"""Configuration settings for the Revenue Analytics Dashboard."""

import os

# File paths
DATA_PATH = os.path.join(os.getcwd(), "new_file.zip")  # Downloaded ZIP file
EXTRACT_DIR = os.path.join(os.getcwd(), "extracted_data")  # Extracted data folder

# Project paths
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))  # Updated for deployment
MODELS_DIR = os.path.join(PROJECT_ROOT, "src/models")

# Model file paths
MODEL_PATH = os.path.join(MODELS_DIR, "revenue_model.joblib")
FEATURE_IMPORTANCE_PATH = os.path.join(MODELS_DIR, "feature_importance.joblib")
TOP_FEATURES_PATH = os.path.join(MODELS_DIR, "top_features.joblib")

# Page configuration
PAGE_CONFIG = {
    "page_title": "Revenue Analytics Dashboard",
    "page_icon": "💰",
    "layout": "wide"
}

# Analytics settings
GEOGRAPHIC_COLUMNS = [
    'geoNetwork.continent',
    'geoNetwork.subContinent',
    'geoNetwork.country',
    'geoNetwork.region',
    'geoNetwork.metro',
    'geoNetwork.city'
]

# Model parameters
MODEL_PARAMS = {
    'n_estimators': 200,
    'learning_rate': 0.05,
    'random_state': 42
}

# Google Drive File ID
GDRIVE_FILE_ID = "1sy1iPPr8mWMcU5Q8hiv6n5YETn2Rw5o8"

