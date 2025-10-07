from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.figure_factory as ff
import streamlit as st

from utils.data import load_data, apply_common_filters, get_distinct_values


st.set_page_config(page_title="Fixed Income & Credit", page_icon="💵", layout="wide")

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
    st.title("Fixed Income & Credit Analysis")
    df = load_data(DATA_PATH)
    countries, ratings, date_filter = sidebar_filters(df)
    fdf = apply_common_filters(df, countries, ratings, date_filter)

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("10Y Bond Yield (%) by Country")
        if {"Country", "Bond_Yield_10Y_Percent"}.issubset(fdf.columns):
            fig = px.bar(
                fdf.sort_values("Bond_Yield_10Y_Percent", ascending=False),
                x="Country",
                y="Bond_Yield_10Y_Percent",
                color="Bond_Yield_10Y_Percent",
                color_continuous_scale="Inferno",
            )
            st.plotly_chart(fig, use_container_width=True)
            st.markdown("**Insights**: Higher yield often reflects higher inflation or risk.")
            st.markdown("**Conclusion**: Each country’s yield shows a different risk/return mix.")

    with col2:
        st.subheader("Bond Yield vs Inflation")
        needed = {"Bond_Yield_10Y_Percent", "Inflation_Rate_Percent", "Country"}
        if needed.issubset(fdf.columns):
            fig = px.scatter(
                fdf,
                x="Inflation_Rate_Percent",
                y="Bond_Yield_10Y_Percent",
                color="Country",
                trendline="ols",
            )
            st.plotly_chart(fig, use_container_width=True)
            st.markdown("**Insights**: Where inflation is higher, yields are often higher.")
            st.markdown("**Conclusion**: Long-term bonds fit better where inflation is stable.")

    col3, col4 = st.columns(2)
    with col3:
        st.subheader("Yield vs Policy Rate")
        needed = {"Bond_Yield_10Y_Percent", "Interest_Rate_Percent", "Country"}
        if needed.issubset(fdf.columns):
            fig = px.scatter(
                fdf,
                x="Interest_Rate_Percent",
                y="Bond_Yield_10Y_Percent",
                color="Country",
            )
            st.plotly_chart(fig, use_container_width=True)
            st.markdown("**Insights**: Policy rate changes affect yields, but not exactly the same amount.")
            st.markdown("**Conclusion**: Watch central bank guidance.")

    with col4:
        st.subheader("Credit Rating Distribution")
        if {"Credit_Rating"}.issubset(fdf.columns):
            fig = px.histogram(fdf, x="Credit_Rating", color="Credit_Rating")
            st.plotly_chart(fig, use_container_width=True)
            st.markdown("**Insights**: Many countries are in investment-grade ratings.")
            st.markdown("**Conclusion**: Ratings can fall; stay updated.")

    col5, col6 = st.columns(2)
    with col5:
        st.subheader("Debt-to-GDP vs Yield")
        needed = {"Government_Debt_GDP_Percent", "Bond_Yield_10Y_Percent", "Country"}
        if needed.issubset(fdf.columns):
            fig = px.scatter(
                fdf,
                x="Government_Debt_GDP_Percent",
                y="Bond_Yield_10Y_Percent",
                color="Country",
                trendline="ols",
            )
            st.plotly_chart(fig, use_container_width=True)
            st.markdown("**Insights**: Countries with more debt often pay higher yields.")
            st.markdown("**Conclusion**: Managing debt is key for steady long-term returns.")

    with col6:
        st.subheader("Political Risk vs Yield")
        needed = {"Political_Risk_Score", "Bond_Yield_10Y_Percent", "Country"}
        if needed.issubset(fdf.columns):
            fig = px.scatter(
                fdf,
                x="Political_Risk_Score",
                y="Bond_Yield_10Y_Percent",
                color="Country",
            )
            st.plotly_chart(fig, use_container_width=True)
            st.markdown("**Insights**: Higher political risk can lift yields.")
            st.markdown("**Conclusion**: Consider stability when choosing countries.")


if __name__ == "__main__":
    main()


