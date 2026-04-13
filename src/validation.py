"""
Data validation module.
Checks that the uploaded dataset conforms to the expected Superstore schema.
"""

import pandas as pd
from typing import Dict, List, Tuple

REQUIRED_COLUMNS = [
    "order_id",
    "order_date",
    "segment",
    "region",
    "category",
    "sub_category",
    "sales",
    "quantity",
    "discount",
    "profit",
]

RECOMMENDED_COLUMNS = [
    "ship_date",
    "ship_mode",
    "customer_id",
    "customer_name",
    "country",
    "city",
    "state",
    "postal_code",
    "product_id",
    "product_name",
]


def validate_columns(df: pd.DataFrame) -> Tuple[bool, List[str], List[str]]:
    """
    Check whether all required and recommended columns are present.
    Returns (is_valid, missing_required, missing_recommended).
    """
    cols = set(df.columns)
    missing_required = [c for c in REQUIRED_COLUMNS if c not in cols]
    missing_recommended = [c for c in RECOMMENDED_COLUMNS if c not in cols]
    is_valid = len(missing_required) == 0
    return is_valid, missing_required, missing_recommended


def generate_quality_report(df: pd.DataFrame) -> Dict[str, object]:
    """
    Produce a data quality summary including row count, null counts,
    duplicate counts, and dtype overview.
    """
    total_rows = len(df)
    total_cols = len(df.columns)
    null_counts = df.isnull().sum()
    null_cols = null_counts[null_counts > 0].to_dict()
    duplicate_rows = int(df.duplicated().sum())
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    date_cols = df.select_dtypes(include="datetime").columns.tolist()

    return {
        "total_rows": total_rows,
        "total_columns": total_cols,
        "null_columns": null_cols,
        "total_nulls": int(null_counts.sum()),
        "duplicate_rows": duplicate_rows,
        "numeric_columns": numeric_cols,
        "date_columns": date_cols,
    }
