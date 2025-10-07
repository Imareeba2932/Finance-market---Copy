from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.figure_factory as ff
import plotly.graph_objects as go
import streamlit as st

from utils.data import load_data, apply_common_filters, get_distinct_values


st.set_page_config(page_title="Equity Markets", page_icon="📈", layout="wide")

DATA_PATH = str(Path(__file__).resolve().parents[1] / "Global finance data.csv")


def sidebar_filters(df: pd.DataFrame):
    meta = get_distinct_values(df)
    st.sidebar.markdown("### Page Filters")
    countries = st.sidebar.multiselect("Country", options=meta["countries"], default=meta["countries"])
    indices = st.sidebar.multiselect("Stock Index", options=meta["stock_indices"], default=meta["stock_indices"])
    ratings = st.sidebar.multiselect("Credit Rating", options=meta["credit_ratings"], default=meta["credit_ratings"])
    date_values = meta["dates"]
    date_filter = None
    if date_values:
        min_date, max_date = min(date_values), max(date_values)
        date_range = st.sidebar.date_input("Date range", value=(min_date, max_date))
        if isinstance(date_range, tuple) and len(date_range) == 2:
            date_filter = [pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])]
    return countries, indices, ratings, date_filter


def main():
    st.title("Equity Markets Analysis")
    df = load_data(DATA_PATH)
    countries, indices, ratings, date_filter = sidebar_filters(df)
    fdf = apply_common_filters(df, countries, ratings, date_filter)
    if indices:
        fdf = fdf[fdf["Stock_Index"].isin(indices)]

    # 1. Bar: Index Value by Country
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Index Value by Country")
        if {"Country", "Index_Value"}.issubset(fdf.columns):
            fig = px.bar(
                fdf.sort_values("Index_Value", ascending=False),
                x="Country",
                y="Index_Value",
                color="Index_Value",
                color_continuous_scale="Viridis",
                hover_data=["Stock_Index"],
            )
            st.plotly_chart(fig, use_container_width=True)
            st.markdown("**Insights**: A higher index level does not always mean higher returns.")
            st.markdown("**Conclusion**: Do not judge by level alone; check changes and valuations.")

    # 2. Bar: Daily Change (%) by Country with color sign
    with col2:
        st.subheader("Daily Change (%) by Country")
        if {"Country", "Daily_Change_Percent"}.issubset(fdf.columns):
            fig = px.bar(
                fdf,
                x="Country",
                y="Daily_Change_Percent",
                color=(fdf["Daily_Change_Percent"] >= 0).map({True: "Gain", False: "Loss"}),
                color_discrete_map={"Gain": "#2ca02c", "Loss": "#d62728"},
            )
            st.plotly_chart(fig, use_container_width=True)
            st.markdown("**Insights**: Daily results differ by country; green means gain, red means loss.")
            st.markdown("**Conclusion**: Daily moves are short term; also check fundamentals.")

    # 3. Scatter: Market Cap vs Index Value sized by Daily Change
    col3, col4 = st.columns(2)
    with col3:
        st.subheader("Market Cap vs Index Value")
        needed = {"Market_Cap_Trillion_USD", "Index_Value", "Daily_Change_Percent", "Country"}
        if needed.issubset(fdf.columns):
            fig = px.scatter(
                fdf,
                x="Index_Value",
                y="Market_Cap_Trillion_USD",
                size="Daily_Change_Percent",
                color="Country",
                hover_data=["Stock_Index"],
            )
            st.plotly_chart(fig, use_container_width=True)
            st.markdown("**Insights**: Big markets do not always move more each day; bubble size shows change.")
            st.markdown("**Conclusion**: Big size does not guarantee low risk; use data to decide.")

    # 4. Treemap: Market Cap by Country and Index
    with col4:
        st.subheader("Market Cap Treemap")
        if {"Country", "Stock_Index", "Market_Cap_Trillion_USD"}.issubset(fdf.columns):
            fig = px.treemap(
                fdf,
                path=["Country", "Stock_Index"],
                values="Market_Cap_Trillion_USD",
                color="Market_Cap_Trillion_USD",
                color_continuous_scale="Blues",
            )
            st.plotly_chart(fig, use_container_width=True)
            st.markdown("**Insights**: You can quickly see which countries and indices hold more market cap.")
            st.markdown("**Conclusion**: Do not stick to only a few big areas; diversify.")

    # 5. Box: Distribution of Index Values
    col5, col6 = st.columns(2)
    with col5:
        st.subheader("Index Value Distribution")
        if {"Index_Value"}.issubset(fdf.columns):
            fig = px.box(fdf, y="Index_Value", points="suspectedoutliers")
            st.plotly_chart(fig, use_container_width=True)
            st.markdown("**Insights**: This shows the middle level and which points are far from the rest.")
            st.markdown("**Conclusion**: Treat extreme values carefully; do not compare them directly.")

    # 6. Heatmap: Correlation between equity metrics
    with col6:
        st.subheader("Equity Metrics Correlation")
        equity_cols = [
            c
            for c in [
                "Index_Value",
                "Daily_Change_Percent",
                "Market_Cap_Trillion_USD",
                "Commodity_Index",
                "Bond_Yield_10Y_Percent",
            ]
            if c in fdf.columns
        ]
        if len(equity_cols) >= 2:
            corr = fdf[equity_cols].corr(numeric_only=True)
            fig = ff.create_annotated_heatmap(
                z=corr.values.round(2),
                x=equity_cols,
                y=equity_cols,
                colorscale="RdBu",
                showscale=True,
                reversescale=True,
            )
            fig.update_layout(margin=dict(l=10, r=10, t=30, b=10))
            st.plotly_chart(fig, use_container_width=True)
            st.markdown("**Insights**: This highlights which numbers move together across countries.")
            st.markdown("**Conclusion**: Lower correlation can make a portfolio more stable.")


if __name__ == "__main__":
    main()


