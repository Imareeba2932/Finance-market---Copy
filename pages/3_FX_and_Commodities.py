from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.figure_factory as ff
import streamlit as st

from utils.data import load_data, apply_common_filters, get_distinct_values


st.set_page_config(page_title="FX & Commodities", page_icon="💱", layout="wide")

DATA_PATH = str(Path(__file__).resolve().parents[1] / "Global finance data.csv")


def sidebar_filters(df: pd.DataFrame):
    meta = get_distinct_values(df)
    st.sidebar.markdown("### Page Filters")
    countries = st.sidebar.multiselect("Country", options=meta["countries"], default=meta["countries"])
    currencies = st.sidebar.multiselect("Currency", options=meta["currencies"], default=meta["currencies"])
    ratings = st.sidebar.multiselect("Credit Rating", options=meta["credit_ratings"], default=meta["credit_ratings"])
    date_values = meta["dates"]
    date_filter = None
    if date_values:
        min_date, max_date = min(date_values), max(date_values)
        date_range = st.sidebar.date_input("Date range", value=(min_date, max_date))
        if isinstance(date_range, tuple) and len(date_range) == 2:
            date_filter = [pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])]
    return countries, currencies, ratings, date_filter


def main():
    st.title("FX & Commodities Analysis")
    df = load_data(DATA_PATH)
    countries, currencies, ratings, date_filter = sidebar_filters(df)
    fdf = apply_common_filters(df, countries, ratings, date_filter)
    if currencies:
        fdf = fdf[fdf["Currency_Code"].isin(currencies)]

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Exchange Rate vs USD")
        needed = {"Country", "Currency_Code", "Exchange_Rate_USD"}
        if needed.issubset(fdf.columns):
            fig = px.bar(
                fdf.sort_values("Exchange_Rate_USD", ascending=False),
                x="Currency_Code",
                y="Exchange_Rate_USD",
                color="Country",
            )
            st.plotly_chart(fig, use_container_width=True)
            st.markdown("**Insights**: A higher number means the local currency is weaker versus USD.")
            st.markdown("**Conclusion**: Currency moves change import costs; keep an eye on it.")

    with col2:
        st.subheader("Currency Change YTD (%)")
        if {"Currency_Code", "Currency_Change_YTD_Percent"}.issubset(fdf.columns):
            fig = px.bar(
                fdf,
                x="Currency_Code",
                y="Currency_Change_YTD_Percent",
                color=(fdf["Currency_Change_YTD_Percent"] >= 0).map({True: "Up", False: "Down"}),
                color_discrete_map={"Up": "#2ca02c", "Down": "#d62728"},
            )
            st.plotly_chart(fig, use_container_width=True)
            st.markdown("**Insights**: Some currencies strengthened this year, others weakened.")
            st.markdown("**Conclusion**: Consider currency effects when investing internationally.")

    col3, col4 = st.columns(2)
    with col3:
        st.subheader("Oil Price vs Commodity Index")
        needed = {"Oil_Price_USD_Barrel", "Commodity_Index", "Country"}
        if needed.issubset(fdf.columns):
            fig = px.scatter(
                fdf,
                x="Commodity_Index",
                y="Oil_Price_USD_Barrel",
                color="Country",
            )
            st.plotly_chart(fig, use_container_width=True)
            st.markdown("**Insights**: Oil prices often move with broader commodities.")
            st.markdown("**Conclusion**: Do not rely only on oil; keep a mix.")

    with col4:
        st.subheader("Gold Price (USD/Oz) by Country")
        needed = {"Gold_Price_USD_Ounce", "Country"}
        if needed.issubset(fdf.columns):
            fig = px.violin(fdf, y="Gold_Price_USD_Ounce", color="Country", box=True, points=False)
            st.plotly_chart(fig, use_container_width=True)
            st.markdown("**Insights**: Gold prices are mostly similar; sometimes they differ.")
            st.markdown("**Conclusion**: Gold can add stability to a portfolio.")

    col5, col6 = st.columns(2)
    with col5:
        st.subheader("FX Heatmap: Rate & YTD Change")
        cols = [c for c in ["Exchange_Rate_USD", "Currency_Change_YTD_Percent"] if c in fdf.columns]
        if len(cols) == 2:
            corr = fdf[cols].corr(numeric_only=True)
            fig = ff.create_annotated_heatmap(z=corr.values.round(2), x=cols, y=cols, colorscale="Blues", showscale=True)
            st.plotly_chart(fig, use_container_width=True)
            st.markdown("**Insights**: FX level and yearly change are related, but not perfectly.")
            st.markdown("**Conclusion**: Look at both to form a currency view.")

    with col6:
        st.subheader("Commodity vs Macro: Inflation")
        needed = {"Commodity_Index", "Inflation_Rate_Percent"}
        if needed.issubset(fdf.columns):
            fig = px.scatter(
                fdf,
                x="Commodity_Index",
                y="Inflation_Rate_Percent",
                color="Country",
                trendline="ols",
            )
            st.plotly_chart(fig, use_container_width=True)
            st.markdown("**Insights**: When commodities get expensive, inflation can rise.")
            st.markdown("**Conclusion**: Watch prices and policies in such times.")


if __name__ == "__main__":
    main()


