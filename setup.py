from setuptools import setup, find_packages

# Read requirements
with open('requirements.txt') as f:
    required = f.read().splitlines()

# Read README for long description
with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="google-analytics-revenue-prediction",
    version="1.0.0",
    author="Varsha Dewangan",
    author_email="varshadewangan1605@gmail.com", 
    description="A comprehensive analytics and prediction system for customer revenue analysis using Google Merchandise Store data",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Varsha-1605/Google-Analytics-Customer-Revenue-Prediction-Project",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Business/Analytics",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Business Intelligence",
        "Framework :: Streamlit",
        "Intended Audience :: Financial and Insurance Industry",
        "Natural Language :: English",
    ],
    python_requires=">=3.11.9",
    install_requires=required,
    entry_points={
        'console_scripts': [
            'revenue-analytics=main:main',
        ],
    },
    include_package_data=True,
    package_data={
        '': ['*.json', '*.yaml', '*.yml', '*.txt'],
    },
    extras_require={
        'dev': [
            'pytest>=6.0',
            'pytest-cov>=2.0',
            'flake8>=3.9.0',
            'black>=21.0',
            'isort>=5.0',
            'mypy>=0.900',
        ],
        'docs': [
            'sphinx>=4.0',
            'sphinx-rtd-theme>=0.5',
            'sphinx-autodoc-typehints>=1.12',
        ],
    },
    project_urls={
        'Bug Reports': 'https://github.com/Varsha-1605/Google-Analytics-Customer-Revenue-Prediction-Project/issues',
        'Source': 'https://github.com/Varsha-1605/Google-Analytics-Customer-Revenue-Prediction-Project',
    },
)