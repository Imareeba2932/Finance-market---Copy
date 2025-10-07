import os
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from utils.data import load_data, apply_common_filters, get_distinct_values


st.set_page_config(
    page_title="Global Finance Dashboard",
    page_icon="💹",
    layout="wide",
    initial_sidebar_state="expanded",
)


DATA_PATH = str(Path(__file__).with_name("Global finance data.csv"))


@st.cache_data(show_spinner=False)
def compute_kpis(df: pd.DataFrame) -> dict:
    kpis = {}
    if "Market_Cap_Trillion_USD" in df.columns:
        kpis["Total Market Cap (T$)"] = round(df["Market_Cap_Trillion_USD"].sum(), 2)
    if "GDP_Growth_Rate_Percent" in df.columns:
        kpis["Avg GDP Growth (%)"] = round(df["GDP_Growth_Rate_Percent"].mean(), 2)
    if "Inflation_Rate_Percent" in df.columns:
        kpis["Avg Inflation (%)"] = round(df["Inflation_Rate_Percent"].mean(), 2)
    if "Bond_Yield_10Y_Percent" in df.columns:
        kpis["Avg 10Y Yield (%)"] = round(df["Bond_Yield_10Y_Percent"].mean(), 2)
    return kpis


def sidebar_filters(df: pd.DataFrame):
    meta = get_distinct_values(df)
    st.sidebar.markdown("### Filters")
    countries = st.sidebar.multiselect("Country", options=meta["countries"], default=meta["countries"])
    ratings = st.sidebar.multiselect("Credit Rating", options=meta["credit_ratings"], default=meta["credit_ratings"])
    date_values = meta["dates"]
    date_filter = None
    if date_values:
        min_date, max_date = min(date_values), max(date_values)
        date_range = st.sidebar.date_input("Date range", value=(min_date, max_date))
        # Convert to pandas timestamps
        if isinstance(date_range, tuple) and len(date_range) == 2:
            date_filter = [pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])]
    return countries, ratings, date_filter


def main():
    st.title("Global Finance Dashboard")
    st.caption("Interactive multi-page analytics built with Streamlit and Plotly")

    df = load_data(DATA_PATH)
    countries, ratings, date_filter = sidebar_filters(df)
    fdf = apply_common_filters(df, countries, ratings, date_filter)

    kpis = compute_kpis(fdf)
    kpi_cols = st.columns(len(kpis) or 1)
    for i, (label, value) in enumerate(kpis.items()):
        with kpi_cols[i]:
            st.metric(label, value)

    st.markdown("---")

    col1, col2 = st.columns([2, 1])
    with col1:
        st.subheader("Market Cap by Country (T$)")
        if {"Country", "Market_Cap_Trillion_USD"}.issubset(fdf.columns):
            fig = px.bar(
                fdf.sort_values("Market_Cap_Trillion_USD", ascending=False),
                x="Country",
                y="Market_Cap_Trillion_USD",
                color="Market_Cap_Trillion_USD",
                color_continuous_scale="Blues",
            )
            fig.update_layout(margin=dict(l=10, r=10, t=30, b=10))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Market cap data not available.")

    with col2:
        st.subheader("Dataset Snapshot")
        st.dataframe(fdf.head(20), use_container_width=True)

    st.markdown("---")

    st.subheader("Key Relationships")
    plot_cols = st.columns(2)
    with plot_cols[0]:
        if {"Index_Value", "Daily_Change_Percent", "Country"}.issubset(fdf.columns):
            fig = px.scatter(
                fdf,
                x="Index_Value",
                y="Daily_Change_Percent",
                color="Country",
                hover_data=["Stock_Index"],
                trendline="ols",
            )
            st.plotly_chart(fig, use_container_width=True)
            st.markdown("**Insights**: A big index number does not always mean a big daily move.")
            st.markdown("**Conclusion**: Day-to-day moves vary; do not assume size controls moves.")
    with plot_cols[1]:
        if {"GDP_Growth_Rate_Percent", "Inflation_Rate_Percent"}.issubset(fdf.columns):
            fig = px.scatter(
                fdf,
                x="Inflation_Rate_Percent",
                y="GDP_Growth_Rate_Percent",
                color="Country",
                trendline="ols",
            )
            st.plotly_chart(fig, use_container_width=True)
            st.markdown("**Insights**: The link between inflation and growth differs by country.")
            st.markdown("**Conclusion**: Compare countries separately; one rule does not fit all.")

    plot_cols2 = st.columns(2)
    with plot_cols2[0]:
        if {"Bond_Yield_10Y_Percent", "Interest_Rate_Percent"}.issubset(fdf.columns):
            fig = px.scatter(
                fdf,
                x="Interest_Rate_Percent",
                y="Bond_Yield_10Y_Percent",
                color="Country",
            )
            st.plotly_chart(fig, use_container_width=True)
            st.markdown("**Insights**: Higher policy rates usually come with higher long-term yields.")
            st.markdown("**Conclusion**: They do not move one-for-one; gaps can remain.")
    with plot_cols2[1]:
        st.empty()


if __name__ == "__main__":
    main()


