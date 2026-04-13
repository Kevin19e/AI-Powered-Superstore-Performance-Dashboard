"""
Export utilities for downloading data and KPI summaries as CSV.
"""

import pandas as pd
from typing import Dict, Any


def dataframe_to_csv_bytes(df: pd.DataFrame) -> bytes:
    """Convert a DataFrame to CSV bytes for Streamlit download."""
    return df.to_csv(index=False).encode("utf-8")


def kpis_to_csv_bytes(kpis: Dict[str, Any]) -> bytes:
    """Convert a KPI dictionary to a downloadable CSV."""
    rows = []
    labels = {
        "total_revenue": ("Total Revenue", "${:,.2f}"),
        "total_profit": ("Total Profit", "${:,.2f}"),
        "total_orders": ("Total Orders", "{:,}"),
        "avg_order_value": ("Average Order Value", "${:,.2f}"),
        "profit_margin": ("Profit Margin", "{:.1f}%"),
        "avg_discount": ("Average Discount", "{:.1f}%"),
        "top_region_sales": ("Top Region (Sales)", "{}"),
        "worst_region_profit": ("Weakest Region (Profit)", "{}"),
        "best_category_profit": ("Best Category (Profit)", "{}"),
        "worst_subcat_profit": ("Worst Sub-Category (Profit)", "{}"),
    }
    for key, (label, fmt) in labels.items():
        if key in kpis:
            rows.append({"KPI": label, "Value": fmt.format(kpis[key])})

    return pd.DataFrame(rows).to_csv(index=False).encode("utf-8")
