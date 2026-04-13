"""
Preprocessing pipeline for Superstore data.
Standardizes column names, parses dates, converts types, and cleans data.
"""

import pandas as pd
from typing import Dict, Tuple

# Maps common Superstore column name variants to the standardized schema.
COLUMN_MAP = {
    # order info
    "order id": "order_id",
    "row id": "row_id",
    "order date": "order_date",
    "ship date": "ship_date",
    "ship mode": "ship_mode",
    # customer info
    "customer id": "customer_id",
    "customer name": "customer_name",
    # geography
    "postal code": "postal_code",
    # product info
    "product id": "product_id",
    "product name": "product_name",
    "sub-category": "sub_category",
    "sub category": "sub_category",
    "subcategory": "sub_category",
}


def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize column names to snake_case standard schema."""
    df = df.copy()
    # First pass: lowercase and strip whitespace
    df.columns = df.columns.str.strip().str.lower()
    # Second pass: apply the mapping for multi-word columns
    df.columns = [COLUMN_MAP.get(c, c.replace(" ", "_").replace("-", "_")) for c in df.columns]
    return df


def parse_dates(df: pd.DataFrame) -> pd.DataFrame:
    """Safely parse date columns to datetime."""
    df = df.copy()
    for col in ["order_date", "ship_date"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce", dayfirst=False)
    return df


def convert_numeric(df: pd.DataFrame) -> pd.DataFrame:
    """Ensure numeric columns are properly typed."""
    df = df.copy()
    numeric_cols = ["sales", "quantity", "discount", "profit"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def clean_text(df: pd.DataFrame) -> pd.DataFrame:
    """Standardize text columns: strip whitespace, title-case categories."""
    df = df.copy()
    text_cols = ["segment", "region", "category", "sub_category", "ship_mode"]
    for col in text_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip().str.title()
    if "country" in df.columns:
        df["country"] = df["country"].astype(str).str.strip().str.title()
    return df


def remove_duplicates(df: pd.DataFrame) -> Tuple[pd.DataFrame, int]:
    """Remove exact duplicate rows. Returns cleaned df and count removed."""
    before = len(df)
    df = df.drop_duplicates().reset_index(drop=True)
    removed = before - len(df)
    return df, removed


def handle_missing(df: pd.DataFrame) -> pd.DataFrame:
    """Fill or drop missing values with business-appropriate defaults."""
    df = df.copy()
    # Fill missing postal codes with 0 (common in Superstore variants)
    if "postal_code" in df.columns:
        df["postal_code"] = df["postal_code"].fillna(0).astype(int)
    # Drop rows where critical business fields are null
    critical = ["sales", "profit", "order_date"]
    existing_critical = [c for c in critical if c in df.columns]
    df = df.dropna(subset=existing_critical).reset_index(drop=True)
    return df


def run_preprocessing(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, object]]:
    """
    Full preprocessing pipeline. Returns the cleaned DataFrame
    and a summary dict of all transformations applied.
    """
    summary: Dict[str, object] = {}

    summary["original_rows"] = len(df)
    summary["original_columns"] = list(df.columns)

    df = standardize_columns(df)
    summary["standardized_columns"] = list(df.columns)

    df = parse_dates(df)
    df = convert_numeric(df)
    df = clean_text(df)

    df, dup_count = remove_duplicates(df)
    summary["duplicates_removed"] = dup_count

    nulls_before = int(df.isnull().sum().sum())
    df = handle_missing(df)
    nulls_after = int(df.isnull().sum().sum())
    summary["nulls_handled"] = nulls_before - nulls_after

    summary["final_rows"] = len(df)
    summary["rows_removed"] = summary["original_rows"] - summary["final_rows"]

    return df, summary
