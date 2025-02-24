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
import gdown

# Google Drive File ID (Extracted from your link)
GDRIVE_FILE_ID = "1sy1iPPr8mWMcU5Q8hiv6n5YETn2Rw5o8"
# Define the destination path
DATA_PATH = os.path.join(os.getcwd(), "new_file.zip")
# Ensure file exists
# Download the file
gdown.download(f"https://drive.google.com/uc?id={GDRIVE_FILE_ID}", DATA_PATH, quiet=False)

# Verify the downloaded file
if os.path.exists(DATA_PATH):
    print("✅ File downloaded successfully.")
else:
    print("❌ Download failed.")

# Project paths
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(PROJECT_ROOT, "models")

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
