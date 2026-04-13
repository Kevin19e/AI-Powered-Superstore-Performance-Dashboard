# AI-Powered Superstore Performance Dashboard

A production-grade business intelligence application that transforms raw retail data into actionable insights. Built as a portfolio project demonstrating end-to-end data analytics capabilities — from data cleaning to KPI design to automated insight generation.

![Python](https://img.shields.io/badge/Python-3.9+-blue?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-FF4B4B?logo=streamlit&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-2.0+-150458?logo=pandas&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-5.18+-3F4F75?logo=plotly&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)

---

## Business Problem

Retail and distribution companies generate thousands of order records daily, yet most teams struggle to:
- Identify which regions, categories, or products drive — or destroy — profitability
- Detect when discount strategies erode margin instead of boosting volume
- Surface underperformance early enough to act on it
- Communicate data-driven findings to non-technical stakeholders

This dashboard solves that by providing an **automated analytics layer** on top of standard transactional data — turning raw CSVs into KPI cards, trend charts, risk flags, and plain-English business recommendations.

## Why This Dataset

The [Kaggle Superstore Dataset](https://www.kaggle.com/datasets/vivek468/superstore-dataset-final) is one of the most widely used retail analytics datasets because it mirrors real-world complexity:
- **Multi-dimensional**: orders span regions, segments, categories, sub-categories, and individual products
- **Profit & discount interplay**: the dataset captures scenarios where aggressive discounting leads to negative margins — a classic retail analytics challenge
- **Temporal depth**: multiple years of order data enable trend analysis
- **Realistic scale**: ~10K records, similar to what a mid-market company would analyze monthly

Unlike toy datasets, Superstore rewards genuine analytical thinking — identifying that "Tables" sub-category consistently loses money, or that the Central region's discount rates undermine its strong sales, mirrors the kind of insight a real analyst would deliver.

## Solution Overview

```
┌─────────────────────────────────────────────────────────┐
│                    Streamlit Frontend                     │
│  KPI Cards │ Trend Charts │ Insights │ Risk Flags │ Export│
├─────────────────────────────────────────────────────────┤
│                    Analytics Engine                       │
│  metrics.py │ insights.py │ charts.py                    │
├─────────────────────────────────────────────────────────┤
│                    Data Pipeline                         │
│  data_loader.py │ preprocess.py │ validation.py          │
├─────────────────────────────────────────────────────────┤
│                    Data Source                            │
│  Kaggle Superstore CSV (upload or default sample)        │
└─────────────────────────────────────────────────────────┘
```

The application follows a **three-layer architecture**:

1. **Data Pipeline**: loads, validates, standardizes, and cleans the raw CSV — handling column name variants, date parsing, type coercion, duplicates, and missing values
2. **Analytics Engine**: computes KPIs, generates aggregations, produces business insights, and identifies risk anomalies
3. **Presentation Layer**: renders everything in a clean, tabbed Streamlit dashboard with interactive Plotly charts

## Features

### Data Handling
- CSV upload or default sample file loading
- Automatic column name standardization (handles Superstore naming variants)
- Date parsing, type coercion, duplicate removal, null handling
- Data quality summary panel with transformation audit trail

### KPI Dashboard
- 10 core business KPIs displayed as styled metric cards
- Real-time recalculation based on active filters

### Interactive Visualizations
- Monthly sales and profit trends
- Regional sales and profit comparison
- Category and sub-category breakdown
- Top 10 products by sales and profit
- Discount vs. profit scatter analysis
- Customer segment contribution (donut chart)
- State-level geographic performance

### Business Insight Engine
- Automated plain-English insight generation
- Identifies revenue drivers, margin risks, and discount impact
- Detects loss-making sub-categories and declining profit trends
- Optional AI-powered executive summary via Google Gemini API

### Risk & Anomaly Detection
- Flags high-discount / negative-profit sub-categories
- Identifies loss-making order rates
- Detects high-sales / weak-margin regions
- Highlights unusually low-performing months

### Filtering & Export
- Filter by date range, region, category, sub-category, segment, and state
- Download filtered dataset as CSV
- Download KPI summary as CSV

## KPI Definitions

| KPI | Definition |
|-----|-----------|
| Total Revenue | Sum of all sales values in the filtered dataset |
| Total Profit | Sum of all profit values in the filtered dataset |
| Total Orders | Count of unique Order IDs |
| Avg Order Value | Total Revenue / Total Orders |
| Profit Margin | (Total Profit / Total Revenue) × 100 |
| Avg Discount | Mean discount percentage across all line items |
| Top Region (Sales) | Region with the highest total sales |
| Weakest Region (Profit) | Region with the lowest total profit |
| Best Category (Profit) | Product category with the highest total profit |
| Worst Sub-Category (Profit) | Sub-category with the lowest total profit |

## Screenshots

> Add screenshots after first run:
> - `assets/dashboard_overview.png` — Full KPI + trends view
> - `assets/architecture.png` — System architecture diagram

## How to Run Locally

### Prerequisites
- Python 3.9 or higher
- pip package manager

### Setup

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/superstore-performance-dashboard.git
cd superstore-performance-dashboard

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Get the Dataset

1. Download from [Kaggle Superstore Dataset](https://www.kaggle.com/datasets/vivek468/superstore-dataset-final)
2. Place the CSV file as `data/raw/SampleSuperstore.csv`
3. Or use the in-app upload feature

### Run

```bash
streamlit run app.py
```

The dashboard will open at `http://localhost:8501`.

### Optional: AI Executive Summary

To enable the Gemini-powered executive summary:
1. Get a free API key from [Google AI Studio](https://aistudio.google.com/apikey)
2. Enter it in the sidebar field when running the app

## Example Business Insights

These are real insights the dashboard generates from the Superstore data:

- **West** drives the most revenue, contributing **31.6%** of total sales
- **Central** is the weakest region by profit ($39,706), signaling potential margin or discount issues
- Sub-categories with high sales but thin margins: **Tables**, **Bookcases** — review pricing or discount policies
- Average discount is **15.6%**, which is above the 15% threshold — aggressive discounting may be eroding profitability
- Loss-making sub-categories: **Tables**, **Bookcases**, **Supplies** — these require urgent strategic review
- The **Consumer** segment contributes **50.6%** of total revenue
- Profit trend is **improving** over the dataset period

## Project Structure

```
AI-Powered Superstore Performance Dashboard/
├── app.py                          # Main Streamlit application
├── requirements.txt                # Python dependencies
├── README.md                       # Project documentation
├── .gitignore                      # Git ignore rules
├── data/
│   └── raw/
│       └── SampleSuperstore.csv    # Kaggle dataset (not tracked in git)
├── src/
│   ├── __init__.py
│   ├── data_loader.py              # CSV loading utilities
│   ├── preprocess.py               # Data cleaning & standardization
│   ├── validation.py               # Schema validation & quality checks
│   ├── metrics.py                  # KPI calculation engine
│   ├── insights.py                 # Business insight & summary generation
│   ├── charts.py                   # Plotly visualization functions
│   └── export_utils.py             # CSV export helpers
└── assets/
    ├── dashboard_overview.png      # Dashboard screenshot
    └── architecture.png            # Architecture diagram
```

## Future Improvements

- **Forecasting module**: add Prophet or ARIMA-based sales forecasting
- **Customer cohort analysis**: RFM segmentation and retention tracking
- **Streamlit Cloud deployment**: one-click deploy with secrets management
- **Database backend**: replace CSV with SQLite or PostgreSQL for larger datasets
- **Automated email reports**: scheduled PDF/HTML report generation
- **A/B discount simulation**: model the profit impact of discount policy changes
- **Multi-file support**: compare performance across multiple time periods
- **Unit tests**: pytest suite for the data pipeline and metrics engine

## Skills Demonstrated

This project is designed to showcase the following competencies relevant to **Data Analyst**, **BI Analyst**, **Business Analyst**, and **AI Automation** roles:

| Skill Area | What This Project Proves |
|-----------|-------------------------|
| **Python** | Clean, modular, type-hinted code with proper separation of concerns |
| **Pandas** | Data cleaning, aggregation, groupby operations, date handling |
| **Data Cleaning** | Column standardization, type coercion, null handling, deduplication |
| **KPI Design** | Business-relevant metric selection and calculation |
| **Business Analysis** | Translating data into actionable recommendations |
| **Dashboarding** | Interactive, filterable UI with professional styling |
| **Data Visualization** | Chart type selection matched to analytical purpose |
| **Communication** | Plain-English insight generation for non-technical stakeholders |
| **AI Integration** | Optional Gemini-powered executive summary |

---

*Built with Python, Streamlit, Pandas, and Plotly. Data sourced from the [Kaggle Superstore Dataset](https://www.kaggle.com/datasets/vivek468/superstore-dataset-final).*
