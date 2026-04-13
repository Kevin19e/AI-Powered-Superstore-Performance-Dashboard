"""
Data loading utilities for Superstore Performance Dashboard.
Handles CSV upload and default sample file loading.
"""

import pandas as pd
import streamlit as st
from pathlib import Path
from typing import Optional

DATA_DIR = Path(__file__).parent.parent / "data" / "raw"

# Support common Superstore filename variants
_CANDIDATES = [
    "SampleSuperstore.csv",
    "Sample - Superstore.csv",
    "Sample_Superstore.csv",
    "Superstore.csv",
    "superstore.csv",
]


def _find_default_file() -> Optional[Path]:
    """Find the first matching Superstore CSV in the data folder."""
    if DATA_DIR.exists():
        for name in _CANDIDATES:
            path = DATA_DIR / name
            if path.exists():
                return path
        # Fallback: pick any CSV in the folder
        csvs = list(DATA_DIR.glob("*.csv"))
        if csvs:
            return csvs[0]
    return None


DEFAULT_DATA_PATH = _find_default_file()


def load_uploaded_file(uploaded_file: st.runtime.uploaded_file_manager.UploadedFile) -> pd.DataFrame:
    """Parse an uploaded CSV file into a DataFrame."""
    try:
        df = pd.read_csv(uploaded_file, encoding="utf-8")
    except UnicodeDecodeError:
        uploaded_file.seek(0)
        df = pd.read_csv(uploaded_file, encoding="latin-1")
    return df


def load_default_sample() -> Optional[pd.DataFrame]:
    """Load the default Superstore sample CSV from the data folder."""
    if DEFAULT_DATA_PATH and DEFAULT_DATA_PATH.exists():
        try:
            return pd.read_csv(DEFAULT_DATA_PATH, encoding="utf-8")
        except UnicodeDecodeError:
            return pd.read_csv(DEFAULT_DATA_PATH, encoding="latin-1")
    return None


def get_data(uploaded_file: Optional[st.runtime.uploaded_file_manager.UploadedFile] = None) -> Optional[pd.DataFrame]:
    """
    Return a DataFrame from either the uploaded file or the default sample.
    Returns None if neither source is available.
    """
    if uploaded_file is not None:
        return load_uploaded_file(uploaded_file)
    return load_default_sample()
