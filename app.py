"""
AI-Powered Superstore Performance Dashboard
============================================
A production-style BI application built on the Kaggle Superstore dataset.
Run with: streamlit run app.py
"""

import streamlit as st
import pandas as pd

from src.data_loader import get_data, DEFAULT_DATA_PATH
from src.preprocess import run_preprocessing
from src.validation import validate_columns, generate_quality_report
from src.metrics import (
    compute_kpis,
    monthly_trends,
    region_breakdown,
    category_breakdown,
    subcategory_breakdown,
    top_products,
    segment_breakdown,
    discount_profit_data,
    state_performance,
)
from src.insights import generate_business_insights, generate_risk_flags, generate_ai_summary
from src.charts import (
    monthly_sales_trend,
    monthly_profit_trend,
    sales_by_region,
    profit_by_region,
    sales_by_category,
    profit_by_subcategory,
    top_products_chart,
    discount_vs_profit_scatter,
    segment_contribution,
    state_performance_chart,
)
from src.export_utils import dataframe_to_csv_bytes, kpis_to_csv_bytes

# ── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Superstore Performance Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    .kpi-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.2rem;
        border-radius: 0.75rem;
        color: white;
        text-align: center;
    }
    .kpi-card h3 { margin: 0; font-size: 0.85rem; opacity: 0.9; }
    .kpi-card h2 { margin: 0.3rem 0 0 0; font-size: 1.5rem; }
    .kpi-card-alt {
        background: linear-gradient(135deg, #2E86AB 0%, #1B5E7B 100%);
        padding: 1.2rem;
        border-radius: 0.75rem;
        color: white;
        text-align: center;
    }
    .kpi-card-alt h3 { margin: 0; font-size: 0.85rem; opacity: 0.9; }
    .kpi-card-alt h2 { margin: 0.3rem 0 0 0; font-size: 1.5rem; }
    div[data-testid="stMetric"] { background: #f8f9fa; padding: 1rem; border-radius: 0.5rem; }
    .risk-high { color: #DC3545; font-weight: 600; }
    .risk-medium { color: #FFC107; font-weight: 600; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Session State ────────────────────────────────────────────────────────────
if "auto_run" not in st.session_state:
    st.session_state.auto_run = False

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("📊 Superstore Dashboard")
    st.markdown("---")

    st.subheader("Data Source")
    data_source = st.radio(
        "Choose data source:",
        ["Upload CSV", "Use default sample"],
        index=1 if DEFAULT_DATA_PATH and DEFAULT_DATA_PATH.exists() else 0,
    )

    uploaded_file = None
    if data_source == "Upload CSV":
        uploaded_file = st.file_uploader("Upload Superstore CSV", type=["csv"])

    st.markdown("---")

    # Run Full Analysis button — always visible in sidebar
    if st.button("🚀 Run Full Analysis", type="primary", width="stretch"):
        st.session_state.auto_run = True
        st.cache_data.clear()
        st.rerun()

    st.markdown("---")
    st.subheader("AI Summary (Optional)")
    gemini_key = st.text_input("Google AI API Key", type="password", help="Leave blank for rule-based summary")

# ── Load & Preprocess ────────────────────────────────────────────────────────
raw_df = get_data(uploaded_file)

if raw_df is None and not st.session_state.auto_run:
    # ── Landing Page with Run Button ─────────────────────────────────────────
    st.markdown("")
    st.markdown("")
    col_l, col_c, col_r = st.columns([1, 2, 1])
    with col_c:
        st.markdown(
            """
            <div style="text-align:center; padding:3rem 2rem; background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);
                        border-radius:1rem; color:white; margin-bottom:2rem;">
                <h1 style="margin:0; font-size:2.2rem;">📊 Superstore Dashboard</h1>
                <p style="opacity:0.9; font-size:1.1rem; margin-top:0.5rem;">
                    AI-Powered Performance Analysis
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("")
        st.info(
            "No dataset found. Place `SampleSuperstore.csv` in `data/raw/` or upload a CSV in the sidebar, "
            "then click the button below."
        )
        if st.button("🚀 Run Full Analysis", type="primary", width="stretch"):
            st.session_state.auto_run = True
            st.rerun()

        st.markdown("")
        st.markdown(
            "<p style='text-align:center; color:#888; font-size:0.85rem;'>"
            "Download the dataset from "
            "<a href='https://www.kaggle.com/datasets/vivek468/superstore-dataset-final' target='_blank'>"
            "Kaggle Superstore Dataset</a></p>",
            unsafe_allow_html=True,
        )
    st.stop()

elif raw_df is None:
    st.warning(
        "No data available. Please upload a CSV file or place "
        "`SampleSuperstore.csv` in the `data/raw/` folder."
    )
    st.session_state.auto_run = False
    st.stop()

# Data loaded — ensure auto_run stays on for future reruns
st.session_state.auto_run = True

# ── Processing Pipeline with Progress ────────────────────────────────────────
progress_bar = st.progress(0, text="Loading data...")
progress_bar.progress(10, text="Cleaning & standardizing columns...")

df, prep_summary = run_preprocessing(raw_df)
progress_bar.progress(30, text="Validating schema...")

is_valid, missing_req, missing_rec = validate_columns(df)

if not is_valid:
    progress_bar.empty()
    st.error(f"Dataset is missing required columns: {', '.join(missing_req)}")
    st.info("Please upload a valid Superstore-format CSV.")
    st.stop()

progress_bar.progress(50, text="Building filters...")

# ── Sidebar Filters ──────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("---")
    st.subheader("Filters")

    # Date range
    min_date = df["order_date"].min().date()
    max_date = df["order_date"].max().date()
    date_range = st.date_input(
        "Order Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )

    # Region
    regions = ["All"] + sorted(df["region"].dropna().unique().tolist())
    sel_region = st.selectbox("Region", regions)

    # Category
    categories = ["All"] + sorted(df["category"].dropna().unique().tolist())
    sel_category = st.selectbox("Category", categories)

    # Sub-category (dynamic)
    if sel_category != "All":
        subcats = ["All"] + sorted(
            df[df["category"] == sel_category]["sub_category"].dropna().unique().tolist()
        )
    else:
        subcats = ["All"] + sorted(df["sub_category"].dropna().unique().tolist())
    sel_subcat = st.selectbox("Sub-Category", subcats)

    # Segment
    segments = ["All"] + sorted(df["segment"].dropna().unique().tolist())
    sel_segment = st.selectbox("Segment", segments)

    # State
    if "state" in df.columns:
        states = ["All"] + sorted(df["state"].dropna().unique().tolist())
        sel_state = st.selectbox("State", states)
    else:
        sel_state = "All"

# ── Apply Filters ────────────────────────────────────────────────────────────
fdf = df.copy()

if len(date_range) == 2:
    start, end = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1])
    fdf = fdf[(fdf["order_date"] >= start) & (fdf["order_date"] <= end)]

if sel_region != "All":
    fdf = fdf[fdf["region"] == sel_region]
if sel_category != "All":
    fdf = fdf[fdf["category"] == sel_category]
if sel_subcat != "All":
    fdf = fdf[fdf["sub_category"] == sel_subcat]
if sel_segment != "All":
    fdf = fdf[fdf["segment"] == sel_segment]
if sel_state != "All" and "state" in fdf.columns:
    fdf = fdf[fdf["state"] == sel_state]

if fdf.empty:
    st.warning("No data matches the selected filters. Adjust your selections.")
    st.stop()

# ── Compute Metrics ──────────────────────────────────────────────────────────
progress_bar.progress(60, text="Computing KPIs...")
kpis = compute_kpis(fdf)
monthly = monthly_trends(fdf)
region_df = region_breakdown(fdf)
cat_df = category_breakdown(fdf)
subcat_df = subcategory_breakdown(fdf)
top_sales = top_products(fdf, "sales")
top_profit = top_products(fdf, "profit")
seg_df = segment_breakdown(fdf)
disc_df = discount_profit_data(fdf)
state_df = state_performance(fdf)

progress_bar.progress(80, text="Generating insights & risk flags...")
insights = generate_business_insights(fdf, kpis)
risk_flags = generate_risk_flags(fdf)

progress_bar.progress(100, text="Analysis complete!")
progress_bar.empty()

# ── Header ───────────────────────────────────────────────────────────────────
st.title("AI-Powered Superstore Performance Dashboard")
st.caption(
    f"Analyzing **{len(fdf):,}** records | "
    f"Date range: {fdf['order_date'].min().strftime('%b %Y')} – "
    f"{fdf['order_date'].max().strftime('%b %Y')}"
)

# ── KPI Cards ────────────────────────────────────────────────────────────────
st.markdown("### Key Performance Indicators")
c1, c2, c3, c4, c5 = st.columns(5)
with c1:
    st.markdown(
        f'<div class="kpi-card"><h3>Total Revenue</h3><h2>${kpis["total_revenue"]:,.0f}</h2></div>',
        unsafe_allow_html=True,
    )
with c2:
    st.markdown(
        f'<div class="kpi-card"><h3>Total Profit</h3><h2>${kpis["total_profit"]:,.0f}</h2></div>',
        unsafe_allow_html=True,
    )
with c3:
    st.markdown(
        f'<div class="kpi-card-alt"><h3>Profit Margin</h3><h2>{kpis["profit_margin"]:.1f}%</h2></div>',
        unsafe_allow_html=True,
    )
with c4:
    st.markdown(
        f'<div class="kpi-card-alt"><h3>Total Orders</h3><h2>{kpis["total_orders"]:,}</h2></div>',
        unsafe_allow_html=True,
    )
with c5:
    st.markdown(
        f'<div class="kpi-card-alt"><h3>Avg Order Value</h3><h2>${kpis["avg_order_value"]:,.0f}</h2></div>',
        unsafe_allow_html=True,
    )

st.markdown("")
c6, c7, c8, c9, c10 = st.columns(5)
with c6:
    st.metric("Avg Discount", f"{kpis['avg_discount']:.1f}%")
with c7:
    st.metric("Top Region (Sales)", kpis["top_region_sales"])
with c8:
    st.metric("Weakest Region (Profit)", kpis["worst_region_profit"])
with c9:
    st.metric("Best Category (Profit)", kpis["best_category_profit"])
with c10:
    st.metric("Worst Sub-Cat (Profit)", kpis["worst_subcat_profit"])

# ── Tabs ─────────────────────────────────────────────────────────────────────
tab_trends, tab_breakdown, tab_products, tab_insights, tab_risk, tab_data, tab_export = st.tabs(
    ["Trends", "Breakdown", "Products", "Insights", "Risk Flags", "Data Quality", "Export"]
)

# ── Tab: Trends ──────────────────────────────────────────────────────────────
with tab_trends:
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(monthly_sales_trend(monthly), width="stretch")
    with col2:
        st.plotly_chart(monthly_profit_trend(monthly), width="stretch")

    col3, col4 = st.columns(2)
    with col3:
        st.plotly_chart(segment_contribution(seg_df), width="stretch")
    with col4:
        st.plotly_chart(discount_vs_profit_scatter(disc_df), width="stretch")

# ── Tab: Breakdown ───────────────────────────────────────────────────────────
with tab_breakdown:
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(sales_by_region(region_df), width="stretch")
    with col2:
        st.plotly_chart(profit_by_region(region_df), width="stretch")

    col3, col4 = st.columns(2)
    with col3:
        st.plotly_chart(sales_by_category(cat_df), width="stretch")
    with col4:
        st.plotly_chart(profit_by_subcategory(subcat_df), width="stretch")

    if not state_df.empty:
        st.markdown("#### State-Level Performance")
        col5, col6 = st.columns(2)
        with col5:
            fig = state_performance_chart(state_df, "sales")
            if fig:
                st.plotly_chart(fig, width="stretch")
        with col6:
            fig = state_performance_chart(state_df, "profit")
            if fig:
                st.plotly_chart(fig, width="stretch")

# ── Tab: Products ────────────────────────────────────────────────────────────
with tab_products:
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(top_products_chart(top_sales, "sales"), width="stretch")
    with col2:
        st.plotly_chart(top_products_chart(top_profit, "profit"), width="stretch")

# ── Tab: Insights ────────────────────────────────────────────────────────────
with tab_insights:
    st.markdown("### Business Insights")
    for i, insight in enumerate(insights, 1):
        st.markdown(f"{i}. {insight}")

    st.markdown("---")
    st.markdown("### Executive Summary")
    summary = generate_ai_summary(kpis, insights, gemini_key if gemini_key else None)
    st.markdown(summary)
    if not gemini_key:
        st.caption("Rule-based summary. Add a Google AI API key in the sidebar for Gemini-powered insights.")

# ── Tab: Risk Flags ──────────────────────────────────────────────────────────
with tab_risk:
    st.markdown("### Risk & Anomaly Detection")
    if not risk_flags:
        st.success("No significant risk flags detected in the current data selection.")
    else:
        for flag in risk_flags:
            severity_class = "risk-high" if flag["severity"] == "High" else "risk-medium"
            st.markdown(
                f'<span class="{severity_class}">[{flag["severity"]}]</span> '
                f'**{flag["type"]}** — {flag["item"]}: {flag["detail"]}',
                unsafe_allow_html=True,
            )
        st.markdown("---")
        st.markdown(f"**{len(risk_flags)}** risk flag(s) identified in current selection.")

# ── Tab: Data Quality ────────────────────────────────────────────────────────
with tab_data:
    st.markdown("### Data Quality & Cleaning Summary")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Original Rows", f"{prep_summary['original_rows']:,}")
    with col2:
        st.metric("Final Rows", f"{prep_summary['final_rows']:,}")
    with col3:
        st.metric("Rows Removed", f"{prep_summary['rows_removed']:,}")

    col4, col5 = st.columns(2)
    with col4:
        st.metric("Duplicates Removed", f"{prep_summary['duplicates_removed']:,}")
    with col5:
        st.metric("Nulls Handled", f"{prep_summary['nulls_handled']:,}")

    quality = generate_quality_report(df)
    if quality["null_columns"]:
        st.markdown("**Remaining null values by column:**")
        st.json(quality["null_columns"])
    else:
        st.success("No remaining null values in the dataset.")

    if missing_rec:
        st.info(f"Optional columns not found in dataset: {', '.join(missing_rec)}")

    with st.expander("View column mapping"):
        st.markdown("**Standardized columns:**")
        st.code(", ".join(prep_summary["standardized_columns"]))

# ── Tab: Export ──────────────────────────────────────────────────────────────
with tab_export:
    st.markdown("### Export Data")

    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            label="Download Filtered Dataset (CSV)",
            data=dataframe_to_csv_bytes(fdf),
            file_name="superstore_filtered.csv",
            mime="text/csv",
        )
    with col2:
        st.download_button(
            label="Download KPI Summary (CSV)",
            data=kpis_to_csv_bytes(kpis),
            file_name="superstore_kpis.csv",
            mime="text/csv",
        )

    st.markdown("---")
    st.caption(
        f"Filtered dataset: {len(fdf):,} rows | "
        f"Full dataset: {len(df):,} rows"
    )

# ── Footer ───────────────────────────────────────────────────────────────────
st.markdown("---")
st.caption(
    "AI-Powered Superstore Performance Dashboard | "
    "Built with Python, Streamlit, Pandas & Plotly | "
    "Data: Kaggle Superstore Dataset"
)
