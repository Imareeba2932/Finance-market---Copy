import os
from typing import List, Optional

import pandas as pd


def load_data(csv_path: str) -> pd.DataFrame:
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV not found at: {csv_path}")
    df = pd.read_csv(csv_path)
    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    return df


def apply_common_filters(
    df: pd.DataFrame,
    country_options: Optional[List[str]] = None,
    credit_ratings: Optional[List[str]] = None,
    dates: Optional[List[pd.Timestamp]] = None,
) -> pd.DataFrame:
    filtered = df.copy()

    if country_options:
        filtered = filtered[filtered["Country"].isin(country_options)]

    if credit_ratings:
        filtered = filtered[filtered["Credit_Rating"].isin(credit_ratings)]

    if dates:
        if len(dates) == 2 and dates[0] is not None and dates[1] is not None:
            start, end = dates
            filtered = filtered[(filtered["Date"] >= start) & (filtered["Date"] <= end)]
        else:
            filtered = filtered[filtered["Date"].isin(dates)]

    return filtered


def get_distinct_values(df: pd.DataFrame) -> dict:
    return {
        "countries": sorted(df["Country"].dropna().unique().tolist()) if "Country" in df.columns else [],
        "credit_ratings": sorted(df["Credit_Rating"].dropna().unique().tolist()) if "Credit_Rating" in df.columns else [],
        "dates": sorted(df["Date"].dropna().unique().tolist()) if "Date" in df.columns else [],
        "currencies": sorted(df["Currency_Code"].dropna().unique().tolist()) if "Currency_Code" in df.columns else [],
        "stock_indices": sorted(df["Stock_Index"].dropna().unique().tolist()) if "Stock_Index" in df.columns else [],
    }


