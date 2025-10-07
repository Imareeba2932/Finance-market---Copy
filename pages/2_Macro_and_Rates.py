from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.figure_factory as ff
import streamlit as st

from utils.data import load_data, apply_common_filters, get_distinct_values


st.set_page_config(page_title="Macro & Rates", page_icon="📊", layout="wide")

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
    st.title("Macro & Interest Rates Analysis")
    df = load_data(DATA_PATH)
    countries, ratings, date_filter = sidebar_filters(df)
    fdf = apply_common_filters(df, countries, ratings, date_filter)

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("GDP Growth (%)")
        if {"Country", "GDP_Growth_Rate_Percent"}.issubset(fdf.columns):
            fig = px.bar(
                fdf.sort_values("GDP_Growth_Rate_Percent", ascending=False),
                x="Country",
                y="GDP_Growth_Rate_Percent",
                color="GDP_Growth_Rate_Percent",
                color_continuous_scale="Greens",
            )
            st.plotly_chart(fig, use_container_width=True)
            st.markdown("**Insights**: Some countries grow faster, others are steady.")
            st.markdown("**Conclusion**: Fast growth should also be sustainable.")

    with col2:
        st.subheader("Inflation Rate (%)")
        if {"Country", "Inflation_Rate_Percent"}.issubset(fdf.columns):
            fig = px.bar(
                fdf.sort_values("Inflation_Rate_Percent", ascending=False),
                x="Country",
                y="Inflation_Rate_Percent",
                color="Inflation_Rate_Percent",
                color_continuous_scale="OrRd",
            )
            st.plotly_chart(fig, use_container_width=True)
            st.markdown("**Insights**: Inflation is different across countries—some lower, some higher.")
            st.markdown("**Conclusion**: Policies will differ; compare countries to understand.")

    col3, col4 = st.columns(2)
    with col3:
        st.subheader("Policy Interest Rate (%)")
        if {"Country", "Interest_Rate_Percent"}.issubset(fdf.columns):
            fig = px.bar(
                fdf.sort_values("Interest_Rate_Percent", ascending=False),
                x="Country",
                y="Interest_Rate_Percent",
                color="Interest_Rate_Percent",
                color_continuous_scale="PuBu",
            )
            st.plotly_chart(fig, use_container_width=True)
            st.markdown("**Insights**: Higher inflation often comes with higher policy rates.")
            st.markdown("**Conclusion**: Higher rates may mean higher returns but also higher risk.")

    col4, col5, col6 = st.columns(3)
    with col4:
        st.subheader("Unemployment Rate (%) - Box")
        if {"Unemployment_Rate_Percent"}.issubset(fdf.columns):
            fig = px.box(fdf, y="Unemployment_Rate_Percent", points="suspectedoutliers")
            st.plotly_chart(fig, use_container_width=True)
            st.markdown("**Insights**: Some places have more jobs, others have fewer.")
            st.markdown("**Conclusion**: Jobs affect both the economy and policy.")

    with col5:
        st.subheader("Inflation vs GDP Growth")
        needed = {"Inflation_Rate_Percent", "GDP_Growth_Rate_Percent", "Country"}
        if needed.issubset(fdf.columns):
            fig = px.scatter(
                fdf,
                x="Inflation_Rate_Percent",
                y="GDP_Growth_Rate_Percent",
                color="Country",
                trendline="ols",
            )
            st.plotly_chart(fig, use_container_width=True)
            st.markdown("**Insights**: Higher inflation often goes with slower growth.")
            st.markdown("**Conclusion**: Balance policies to control inflation and support growth.")

    with col6:
        st.subheader("Policy Rate vs 10Y Yield")
        needed = {"Interest_Rate_Percent", "Bond_Yield_10Y_Percent", "Country"}
        if needed.issubset(fdf.columns):
            fig = px.scatter(
                fdf,
                x="Interest_Rate_Percent",
                y="Bond_Yield_10Y_Percent",
                color="Country",
            )
            st.plotly_chart(fig, use_container_width=True)
            st.markdown("**Insights**: Policy rate changes affect long-term yields, but not perfectly.")
            st.markdown("**Conclusion**: The yield curve shape gives hints about the future economy.")


if __name__ == "__main__":
    main()


