"""
Business insight engine.
Generates plain-English insights and risk flags from KPIs and aggregated data.
Optionally uses Google Gemini for an executive summary.
"""

import pandas as pd
from typing import Dict, List, Any, Optional


def generate_business_insights(df: pd.DataFrame, kpis: Dict[str, Any]) -> List[str]:
    """Produce a list of plain-English business insights based on the data."""
    insights: List[str] = []

    # Revenue leader
    region_sales = df.groupby("region")["sales"].sum().sort_values(ascending=False)
    if not region_sales.empty:
        top = region_sales.index[0]
        pct = region_sales.iloc[0] / region_sales.sum() * 100
        insights.append(
            f"**{top}** drives the most revenue, contributing **{pct:.1f}%** of total sales."
        )

    # Profit underperformer
    region_profit = df.groupby("region")["profit"].sum().sort_values()
    if not region_profit.empty:
        worst = region_profit.index[0]
        val = region_profit.iloc[0]
        insights.append(
            f"**{worst}** is the weakest region by profit (${val:,.0f}), "
            f"signaling potential margin or discount issues."
        )

    # High-sales, low-margin sub-categories
    subcat = df.groupby("sub_category").agg(sales=("sales", "sum"), profit=("profit", "sum")).reset_index()
    subcat["margin"] = subcat["profit"] / subcat["sales"] * 100
    risky = subcat[(subcat["sales"] > subcat["sales"].median()) & (subcat["margin"] < 5)]
    if not risky.empty:
        names = ", ".join(f"**{r}**" for r in risky["sub_category"].tolist())
        insights.append(
            f"Sub-categories with high sales but thin margins (<5%): {names}. "
            f"Review pricing or discount policies."
        )

    # Discount impact
    avg_disc = kpis["avg_discount"]
    if avg_disc > 15:
        insights.append(
            f"Average discount is **{avg_disc:.1f}%**, which is above the 15% threshold. "
            f"Aggressive discounting may be eroding profitability."
        )
    else:
        insights.append(
            f"Average discount is **{avg_disc:.1f}%**, which appears well controlled."
        )

    # Negative-profit sub-categories
    neg_subcat = subcat[subcat["profit"] < 0]
    if not neg_subcat.empty:
        names = ", ".join(f"**{r}**" for r in neg_subcat["sub_category"].tolist())
        insights.append(
            f"Loss-making sub-categories: {names}. These require urgent strategic review."
        )

    # Segment leader
    seg_sales = df.groupby("segment")["sales"].sum().sort_values(ascending=False)
    if not seg_sales.empty:
        top_seg = seg_sales.index[0]
        seg_pct = seg_sales.iloc[0] / seg_sales.sum() * 100
        insights.append(
            f"The **{top_seg}** segment contributes **{seg_pct:.1f}%** of total revenue."
        )

    # Profit trend direction
    if "order_date" in df.columns:
        monthly = df.set_index("order_date").resample("ME")["profit"].sum()
        if len(monthly) >= 6:
            first_half = monthly.iloc[: len(monthly) // 2].mean()
            second_half = monthly.iloc[len(monthly) // 2 :].mean()
            if second_half > first_half * 1.05:
                insights.append("Profit trend is **improving** over the dataset period.")
            elif second_half < first_half * 0.95:
                insights.append("Profit trend is **declining** over the dataset period, warranting attention.")
            else:
                insights.append("Profit trend is **stable** across the dataset period.")

    return insights


def generate_risk_flags(df: pd.DataFrame) -> List[Dict[str, str]]:
    """Identify risk items: high-discount/low-profit products, negative-profit orders, etc."""
    flags: List[Dict[str, str]] = []

    # Sub-categories with high average discount AND negative profit
    subcat = df.groupby("sub_category").agg(
        avg_discount=("discount", "mean"),
        total_profit=("profit", "sum"),
        total_sales=("sales", "sum"),
    ).reset_index()
    risky = subcat[(subcat["avg_discount"] > 0.2) & (subcat["total_profit"] < 0)]
    for _, row in risky.iterrows():
        flags.append({
            "type": "High Discount + Negative Profit",
            "item": row["sub_category"],
            "detail": (
                f"Avg discount: {row['avg_discount']:.0%}, "
                f"Total profit: ${row['total_profit']:,.0f}"
            ),
            "severity": "High",
        })

    # Negative-profit order count
    neg_orders = df[df["profit"] < 0]
    neg_pct = len(neg_orders) / len(df) * 100 if len(df) > 0 else 0
    if neg_pct > 10:
        flags.append({
            "type": "High Rate of Loss-Making Orders",
            "item": "All regions",
            "detail": f"{len(neg_orders):,} orders ({neg_pct:.1f}%) have negative profit.",
            "severity": "High",
        })
    elif neg_pct > 0:
        flags.append({
            "type": "Loss-Making Orders Present",
            "item": "All regions",
            "detail": f"{len(neg_orders):,} orders ({neg_pct:.1f}%) have negative profit.",
            "severity": "Medium",
        })

    # Regions with strong sales but weak margin
    region = df.groupby("region").agg(sales=("sales", "sum"), profit=("profit", "sum")).reset_index()
    region["margin"] = region["profit"] / region["sales"] * 100
    weak_margin = region[(region["sales"] > region["sales"].median()) & (region["margin"] < 8)]
    for _, row in weak_margin.iterrows():
        flags.append({
            "type": "High Sales, Weak Margin Region",
            "item": row["region"],
            "detail": f"Sales: ${row['sales']:,.0f}, Margin: {row['margin']:.1f}%",
            "severity": "Medium",
        })

    # Low-performing months
    if "order_date" in df.columns:
        monthly_profit = df.set_index("order_date").resample("ME")["profit"].sum()
        if len(monthly_profit) > 3:
            mean_profit = monthly_profit.mean()
            low_months = monthly_profit[monthly_profit < mean_profit * 0.5]
            for month, val in low_months.items():
                flags.append({
                    "type": "Unusually Low-Performing Month",
                    "item": month.strftime("%B %Y"),
                    "detail": f"Profit: ${val:,.0f} (avg: ${mean_profit:,.0f})",
                    "severity": "Medium",
                })

    return flags


def generate_ai_summary(kpis: Dict[str, Any], insights: List[str], api_key: Optional[str] = None) -> str:
    """
    Generate an executive summary. Uses Google Gemini if a key is provided,
    otherwise falls back to a rule-based summary.
    """
    if api_key:
        try:
            return _gemini_summary(kpis, insights, api_key)
        except Exception as e:
            return _rule_based_summary(kpis, insights) + f"\n\n> *AI summary unavailable: {e}*"

    return _rule_based_summary(kpis, insights)


def _gemini_summary(kpis: Dict[str, Any], insights: List[str], api_key: str) -> str:
    """Call Google Gemini API for an executive summary."""
    import google.generativeai as genai

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.0-flash")

    insight_text = "\n".join(f"- {i}" for i in insights)
    prompt = (
        "You are a senior business analyst. Based on the following KPIs and insights "
        "from a retail superstore, write a concise executive summary in exactly 5 bullet points "
        "suitable for a manager. Be specific with numbers. Use markdown bold for key figures.\n\n"
        f"KPIs:\n"
        f"- Total Revenue: ${kpis['total_revenue']:,.0f}\n"
        f"- Total Profit: ${kpis['total_profit']:,.0f}\n"
        f"- Profit Margin: {kpis['profit_margin']:.1f}%\n"
        f"- Total Orders: {kpis['total_orders']:,}\n"
        f"- Avg Discount: {kpis['avg_discount']:.1f}%\n"
        f"- Top Region: {kpis['top_region_sales']}\n"
        f"- Weakest Region (profit): {kpis['worst_region_profit']}\n\n"
        f"Insights:\n{insight_text}"
    )

    response = model.generate_content(
        prompt,
        generation_config=genai.types.GenerationConfig(
            max_output_tokens=400,
            temperature=0.3,
        ),
    )
    return response.text


def _rule_based_summary(kpis: Dict[str, Any], insights: List[str]) -> str:
    """Generate a structured executive summary without an LLM."""
    lines = [
        "**Executive Summary**",
        "",
        f"1. The business generated **${kpis['total_revenue']:,.0f}** in total revenue "
        f"with a profit margin of **{kpis['profit_margin']:.1f}%** across "
        f"**{kpis['total_orders']:,}** orders.",
        "",
        f"2. **{kpis['top_region_sales']}** is the top-performing region by sales "
        f"(${kpis['top_region_sales_value']:,.0f}), while **{kpis['worst_region_profit']}** "
        f"underperforms on profitability (${kpis['worst_region_profit_value']:,.0f}).",
        "",
        f"3. Average discount across the portfolio is **{kpis['avg_discount']:.1f}%**. "
        + (
            "This exceeds the 15% healthy threshold and may be eroding margins."
            if kpis["avg_discount"] > 15
            else "This is within a healthy range."
        ),
        "",
        f"4. **{kpis['best_category_profit']}** is the most profitable category, "
        f"while **{kpis['worst_subcat_profit']}** is the worst-performing sub-category by profit.",
        "",
        f"5. Key recommendation: review discount policies in underperforming regions "
        f"and loss-making sub-categories to protect overall margin.",
    ]
    return "\n".join(lines)
