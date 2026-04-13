"""
KPI calculation engine.
Computes all business metrics from the cleaned Superstore data.
"""

import pandas as pd
from typing import Dict, Any


def compute_kpis(df: pd.DataFrame) -> Dict[str, Any]:
    """Calculate core business KPIs from the cleaned dataset."""
    total_revenue = float(df["sales"].sum())
    total_profit = float(df["profit"].sum())
    total_orders = int(df["order_id"].nunique())
    avg_order_value = total_revenue / total_orders if total_orders > 0 else 0.0
    profit_margin = (total_profit / total_revenue * 100) if total_revenue > 0 else 0.0
    avg_discount = float(df["discount"].mean() * 100)

    # Regional performance
    region_sales = df.groupby("region")["sales"].sum()
    region_profit = df.groupby("region")["profit"].sum()
    top_region_sales = region_sales.idxmax() if not region_sales.empty else "N/A"
    worst_region_profit = region_profit.idxmin() if not region_profit.empty else "N/A"

    # Category performance
    cat_profit = df.groupby("category")["profit"].sum()
    best_category_profit = cat_profit.idxmax() if not cat_profit.empty else "N/A"

    subcat_profit = df.groupby("sub_category")["profit"].sum()
    worst_subcat_profit = subcat_profit.idxmin() if not subcat_profit.empty else "N/A"

    return {
        "total_revenue": total_revenue,
        "total_profit": total_profit,
        "total_orders": total_orders,
        "avg_order_value": avg_order_value,
        "profit_margin": profit_margin,
        "avg_discount": avg_discount,
        "top_region_sales": top_region_sales,
        "worst_region_profit": worst_region_profit,
        "best_category_profit": best_category_profit,
        "worst_subcat_profit": worst_subcat_profit,
        "top_region_sales_value": float(region_sales.max()) if not region_sales.empty else 0.0,
        "worst_region_profit_value": float(region_profit.min()) if not region_profit.empty else 0.0,
    }


def monthly_trends(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate sales and profit by month."""
    df = df.copy()
    df["year_month"] = df["order_date"].dt.to_period("M").dt.to_timestamp()
    monthly = (
        df.groupby("year_month")
        .agg(sales=("sales", "sum"), profit=("profit", "sum"), orders=("order_id", "nunique"))
        .reset_index()
        .sort_values("year_month")
    )
    return monthly


def region_breakdown(df: pd.DataFrame) -> pd.DataFrame:
    """Sales and profit breakdown by region."""
    return (
        df.groupby("region")
        .agg(sales=("sales", "sum"), profit=("profit", "sum"), orders=("order_id", "nunique"))
        .reset_index()
        .sort_values("sales", ascending=False)
    )


def category_breakdown(df: pd.DataFrame) -> pd.DataFrame:
    """Sales and profit breakdown by category."""
    return (
        df.groupby("category")
        .agg(sales=("sales", "sum"), profit=("profit", "sum"))
        .reset_index()
        .sort_values("sales", ascending=False)
    )


def subcategory_breakdown(df: pd.DataFrame) -> pd.DataFrame:
    """Sales and profit breakdown by sub-category."""
    return (
        df.groupby("sub_category")
        .agg(sales=("sales", "sum"), profit=("profit", "sum"), avg_discount=("discount", "mean"))
        .reset_index()
        .sort_values("profit", ascending=True)
    )


def top_products(df: pd.DataFrame, metric: str = "sales", n: int = 10) -> pd.DataFrame:
    """Return top N products by a given metric."""
    return (
        df.groupby("product_name")
        .agg(sales=("sales", "sum"), profit=("profit", "sum"), quantity=("quantity", "sum"))
        .reset_index()
        .sort_values(metric, ascending=False)
        .head(n)
    )


def segment_breakdown(df: pd.DataFrame) -> pd.DataFrame:
    """Sales and profit breakdown by customer segment."""
    return (
        df.groupby("segment")
        .agg(sales=("sales", "sum"), profit=("profit", "sum"), orders=("order_id", "nunique"))
        .reset_index()
        .sort_values("sales", ascending=False)
    )


def discount_profit_data(df: pd.DataFrame) -> pd.DataFrame:
    """Prepare order-level discount vs profit data for scatter analysis."""
    return df[["order_id", "discount", "profit", "sales", "category", "sub_category"]].copy()


def state_performance(df: pd.DataFrame) -> pd.DataFrame:
    """Sales and profit by state (if available)."""
    if "state" not in df.columns:
        return pd.DataFrame()
    return (
        df.groupby("state")
        .agg(sales=("sales", "sum"), profit=("profit", "sum"))
        .reset_index()
        .sort_values("sales", ascending=False)
    )
