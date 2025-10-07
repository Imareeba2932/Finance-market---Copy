from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.figure_factory as ff
import streamlit as st

from utils.data import load_data, apply_common_filters, get_distinct_values


st.set_page_config(page_title="Trade & Real Estate", page_icon="🏠", layout="wide")

DATA_PATH = str(Path(__file__).resolve().parents[1] / "Global finance data.csv")


def sidebar_filters(df: pd.DataFrame):
    meta = get_distinct_values(df)
    st.sidebar.markdown("### Page Filters")
    countries = st.sidebar.multiselect("Country", options=meta["countries"], default=meta["countries"])
    ratings = st.sidebar.multiselect("Credit Rating", options=meta["credit_ratings"], default=meta["credit_ratings"])
    date_values = meta["dates"]
    date_filter = None
    if date_values:
        min_date, max_date = min(date_values), max(date_values)
        date_range = st.sidebar.date_input("Date range", value=(min_date, max_date))
        if isinstance(date_range, tuple) and len(date_range) == 2:
            date_filter = [pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])]
    return countries, ratings, date_filter


def main():
    st.title("Trade & Real Estate Analysis")
    df = load_data(DATA_PATH)
    countries, ratings, date_filter = sidebar_filters(df)
    fdf = apply_common_filters(df, countries, ratings, date_filter)

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Export Growth (%) by Country")
        if {"Country", "Export_Growth_Percent"}.issubset(fdf.columns):
            fig = px.bar(
                fdf.sort_values("Export_Growth_Percent", ascending=False),
                x="Country",
                y="Export_Growth_Percent",
                color="Export_Growth_Percent",
                color_continuous_scale="Greens",
            )
            st.plotly_chart(fig, use_container_width=True)
            st.markdown("**Insights**: Some countries’ exports are growing faster due to strong foreign demand.")
            st.markdown("**Conclusion**: Strong exports help both the economy and the currency.")

    with col2:
        st.subheader("Import Growth (%) by Country")
        if {"Country", "Import_Growth_Percent"}.issubset(fdf.columns):
            fig = px.bar(
                fdf.sort_values("Import_Growth_Percent", ascending=False),
                x="Country",
                y="Import_Growth_Percent",
                color="Import_Growth_Percent",
                color_continuous_scale="Reds",
            )
            st.plotly_chart(fig, use_container_width=True)
            st.markdown("**Insights**: Rising imports can mean strong local demand or currency effects.")
            st.markdown("**Conclusion**: Watch the trade balance (exports minus imports).")

    col3, col4 = st.columns(2)
    with col3:
        st.subheader("Current Account Balance (B$)")
        if {"Country", "Current_Account_Balance_Billion_USD"}.issubset(fdf.columns):
            fig = px.bar(
                fdf.sort_values("Current_Account_Balance_Billion_USD", ascending=False),
                x="Country",
                y="Current_Account_Balance_Billion_USD",
                color="Current_Account_Balance_Billion_USD",
                color_continuous_scale="Blues",
            )
            st.plotly_chart(fig, use_container_width=True)
            st.markdown("**Insights**: A current-account surplus supports a stronger currency.")
            st.markdown("**Conclusion**: Long deficits may need outside funding.")

    with col4:
        st.subheader("FDI Inflow (B$)")
        if {"Country", "FDI_Inflow_Billion_USD"}.issubset(fdf.columns):
            fig = px.bar(
                fdf.sort_values("FDI_Inflow_Billion_USD", ascending=False),
                x="Country",
                y="FDI_Inflow_Billion_USD",
                color="FDI_Inflow_Billion_USD",
                color_continuous_scale="Purples",
            )
            st.plotly_chart(fig, use_container_width=True)
            st.markdown("**Insights**: Stable, growing countries attract more foreign investment.")
            st.markdown("**Conclusion**: Such inflows support long-term growth.")

    col5, col6 = st.columns(2)
    with col5:
        st.subheader("Real Estate Index by Country")
        if {"Country", "Real_Estate_Index"}.issubset(fdf.columns):
            fig = px.box(fdf, x="Country", y="Real_Estate_Index")
            st.plotly_chart(fig, use_container_width=True)
            st.markdown("**Insights**: Property levels differ a lot by country.")
            st.markdown("**Conclusion**: Real estate is local; trends vary by place.")

    with col6:
        st.subheader("Real Estate vs GDP Growth")
        needed = {"Real_Estate_Index", "GDP_Growth_Rate_Percent", "Country"}
        if needed.issubset(fdf.columns):
            fig = px.scatter(
                fdf,
                x="GDP_Growth_Rate_Percent",
                y="Real_Estate_Index",
                color="Country",
                trendline="ols",
            )
            st.plotly_chart(fig, use_container_width=True)
            st.markdown("**Insights**: Better growth often comes with stronger property indices.")
            st.markdown("**Conclusion**: Interest rates and credit also matter a lot.")


if __name__ == "__main__":
    main()


