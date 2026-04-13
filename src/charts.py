"""
Visualization module using Plotly.
All chart functions return Plotly figure objects ready for Streamlit rendering.
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Optional

# Consistent color palette
COLORS = px.colors.qualitative.Set2
PRIMARY = "#2E86AB"
SECONDARY = "#A23B72"
POSITIVE = "#2E8B57"
NEGATIVE = "#DC3545"


def _apply_layout(fig: go.Figure, title: str, height: int = 420) -> go.Figure:
    """Apply a consistent clean layout to all figures."""
    fig.update_layout(
        title=dict(text=title, font=dict(size=16)),
        height=height,
        margin=dict(l=40, r=40, t=60, b=40),
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Segoe UI, sans-serif", size=12),
        legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5),
    )
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor="rgba(200,200,200,0.3)")
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor="rgba(200,200,200,0.3)")
    return fig


def monthly_sales_trend(monthly: pd.DataFrame) -> go.Figure:
    fig = px.line(
        monthly, x="year_month", y="sales",
        markers=True, color_discrete_sequence=[PRIMARY],
    )
    fig.update_traces(line=dict(width=2.5))
    return _apply_layout(fig, "Monthly Sales Trend")


def monthly_profit_trend(monthly: pd.DataFrame) -> go.Figure:
    fig = px.bar(
        monthly, x="year_month", y="profit",
        color_discrete_sequence=[POSITIVE],
    )
    return _apply_layout(fig, "Monthly Profit Trend")


def sales_by_region(region_df: pd.DataFrame) -> go.Figure:
    fig = px.bar(
        region_df, x="region", y="sales",
        color="region", color_discrete_sequence=COLORS,
        text_auto=",.0f",
    )
    fig.update_traces(textposition="outside")
    return _apply_layout(fig, "Sales by Region")


def profit_by_region(region_df: pd.DataFrame) -> go.Figure:
    colors = [POSITIVE if v >= 0 else NEGATIVE for v in region_df["profit"]]
    fig = go.Figure(
        go.Bar(
            x=region_df["region"], y=region_df["profit"],
            marker_color=colors, text=[f"${v:,.0f}" for v in region_df["profit"]],
            textposition="outside",
        )
    )
    return _apply_layout(fig, "Profit by Region")


def sales_by_category(cat_df: pd.DataFrame) -> go.Figure:
    fig = px.bar(
        cat_df, x="category", y="sales",
        color="category", color_discrete_sequence=COLORS,
        text_auto=",.0f",
    )
    fig.update_traces(textposition="outside")
    return _apply_layout(fig, "Sales by Category")


def profit_by_subcategory(subcat_df: pd.DataFrame) -> go.Figure:
    subcat_sorted = subcat_df.sort_values("profit", ascending=True)
    colors = [POSITIVE if v >= 0 else NEGATIVE for v in subcat_sorted["profit"]]
    fig = go.Figure(
        go.Bar(
            y=subcat_sorted["sub_category"], x=subcat_sorted["profit"],
            orientation="h", marker_color=colors,
            text=[f"${v:,.0f}" for v in subcat_sorted["profit"]],
            textposition="outside",
        )
    )
    return _apply_layout(fig, "Profit by Sub-Category", height=500)


def top_products_chart(products_df: pd.DataFrame, metric: str = "sales") -> go.Figure:
    color = PRIMARY if metric == "sales" else POSITIVE
    fig = px.bar(
        products_df.sort_values(metric, ascending=True),
        y="product_name", x=metric, orientation="h",
        color_discrete_sequence=[color],
        text_auto=",.0f",
    )
    fig.update_traces(textposition="outside")
    title = f"Top 10 Products by {'Sales' if metric == 'sales' else 'Profit'}"
    return _apply_layout(fig, title, height=480)


def discount_vs_profit_scatter(df: pd.DataFrame) -> go.Figure:
    fig = px.scatter(
        df, x="discount", y="profit",
        color="category", color_discrete_sequence=COLORS,
        opacity=0.5, hover_data=["sub_category"],
    )
    fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.6)
    return _apply_layout(fig, "Discount vs. Profit (Order Level)")


def segment_contribution(seg_df: pd.DataFrame) -> go.Figure:
    fig = px.pie(
        seg_df, values="sales", names="segment",
        color_discrete_sequence=COLORS,
        hole=0.4,
    )
    fig.update_traces(textinfo="label+percent", textposition="outside")
    return _apply_layout(fig, "Revenue by Customer Segment", height=400)


def state_performance_chart(state_df: pd.DataFrame, metric: str = "sales") -> Optional[go.Figure]:
    if state_df.empty:
        return None
    top_states = state_df.sort_values(metric, ascending=False).head(15)
    fig = px.bar(
        top_states.sort_values(metric, ascending=True),
        y="state", x=metric, orientation="h",
        color_discrete_sequence=[PRIMARY if metric == "sales" else POSITIVE],
        text_auto=",.0f",
    )
    fig.update_traces(textposition="outside")
    title = f"Top 15 States by {'Sales' if metric == 'sales' else 'Profit'}"
    return _apply_layout(fig, title, height=500)
