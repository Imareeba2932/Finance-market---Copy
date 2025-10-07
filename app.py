from pathlib import Path
from typing import List, Optional, Tuple

from flask import Flask, render_template, request
import pandas as pd
import plotly.express as px
import plotly.figure_factory as ff
from plotly.offline import plot as plotly_plot

from flask_utils.data import load_data, apply_common_filters, get_distinct_values


app = Flask(__name__)


DATA_PATH = str(Path(__file__).with_name("Global finance data.csv"))


def _get_query_params(meta: dict, include: Optional[List[str]] = None) -> Tuple[List[str], List[str], Optional[List[pd.Timestamp]]]:
    include = include or []
    countries = request.args.getlist("country") or meta.get("countries", [])
    ratings = request.args.getlist("rating") or meta.get("credit_ratings", [])
    # Date range
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    date_filter = None
    if start_date and end_date:
        try:
            date_filter = [pd.to_datetime(start_date), pd.to_datetime(end_date)]
        except Exception:
            date_filter = None
    return countries, ratings, date_filter


def _plot_div(fig) -> str:
    fig.update_layout(margin=dict(l=10, r=10, t=30, b=10))
    return plotly_plot(fig, output_type="div", include_plotlyjs=False, show_link=False, config={"displayModeBar": True})


@app.route("/")
def home():
    df = load_data(DATA_PATH)
    meta = get_distinct_values(df)
    countries, ratings, date_filter = _get_query_params(meta)
    fdf = apply_common_filters(df, countries, ratings, date_filter)

    # KPIs
    kpis = {}
    if "Market_Cap_Trillion_USD" in fdf.columns:
        kpis["Total Market Cap (T$)"] = round(float(fdf["Market_Cap_Trillion_USD"].sum()), 2)
    if "GDP_Growth_Rate_Percent" in fdf.columns:
        kpis["Avg GDP Growth (%)"] = round(float(fdf["GDP_Growth_Rate_Percent"].mean()), 2)
    if "Inflation_Rate_Percent" in fdf.columns:
        kpis["Avg Inflation (%)"] = round(float(fdf["Inflation_Rate_Percent"].mean()), 2)
    if "Bond_Yield_10Y_Percent" in fdf.columns:
        kpis["Avg 10Y Yield (%)"] = round(float(fdf["Bond_Yield_10Y_Percent"].mean()), 2)

    market_cap_div = None
    if {"Country", "Market_Cap_Trillion_USD"}.issubset(fdf.columns):
        fig = px.bar(
            fdf.sort_values("Market_Cap_Trillion_USD", ascending=False),
            x="Country",
            y="Market_Cap_Trillion_USD",
            color="Market_Cap_Trillion_USD",
            color_continuous_scale="Blues",
        )
        market_cap_div = _plot_div(fig)

    rel_scatter1_div = None
    if {"Index_Value", "Daily_Change_Percent", "Country"}.issubset(fdf.columns):
        fig = px.scatter(
            fdf,
            x="Index_Value",
            y="Daily_Change_Percent",
            color="Country",
            hover_data=["Stock_Index"],
            trendline="ols",
        )
        rel_scatter1_div = _plot_div(fig)

    rel_scatter2_div = None
    if {"Bond_Yield_10Y_Percent", "Interest_Rate_Percent"}.issubset(fdf.columns):
        fig = px.scatter(
            fdf,
            x="Interest_Rate_Percent",
            y="Bond_Yield_10Y_Percent",
            color="Country",
        )
        rel_scatter2_div = _plot_div(fig)

    return render_template(
        "home.html",
        meta=meta,
        selected={"countries": countries, "ratings": ratings, "start_date": request.args.get("start_date"), "end_date": request.args.get("end_date")},
        kpis=kpis,
        market_cap_div=market_cap_div,
        rel_scatter1_div=rel_scatter1_div,
        rel_scatter2_div=rel_scatter2_div,
        table=fdf.head(20).to_html(classes="table table-sm table-striped", index=False),
    )


@app.route("/equity-markets")
def equity_markets():
    df = load_data(DATA_PATH)
    meta = get_distinct_values(df)
    countries, ratings, date_filter = _get_query_params(meta)
    indices = request.args.getlist("index") or meta.get("stock_indices", [])
    fdf = apply_common_filters(df, countries, ratings, date_filter)
    if indices:
        fdf = fdf[fdf["Stock_Index"].isin(indices)]

    divs = {"bar_index_value": None, "bar_daily_change": None, "scatter_cap_vs_index": None, "treemap_cap": None, "box_index_value": None, "heatmap_corr": None}

    if {"Country", "Index_Value"}.issubset(fdf.columns):
        fig = px.bar(
            fdf.sort_values("Index_Value", ascending=False),
            x="Country",
            y="Index_Value",
            color="Index_Value",
            color_continuous_scale="Viridis",
            hover_data=["Stock_Index"],
        )
        divs["bar_index_value"] = _plot_div(fig)

    if {"Country", "Daily_Change_Percent"}.issubset(fdf.columns):
        fig = px.bar(
            fdf,
            x="Country",
            y="Daily_Change_Percent",
            color=(fdf["Daily_Change_Percent"] >= 0).map({True: "Gain", False: "Loss"}),
            color_discrete_map={"Gain": "#2ca02c", "Loss": "#d62728"},
        )
        divs["bar_daily_change"] = _plot_div(fig)

    needed = {"Market_Cap_Trillion_USD", "Index_Value", "Daily_Change_Percent", "Country"}
    if needed.issubset(fdf.columns):
        size_series = fdf["Daily_Change_Percent"].abs()
        fig = px.scatter(
            fdf.assign(SizeAbs=size_series),
            x="Index_Value",
            y="Market_Cap_Trillion_USD",
            size="SizeAbs",
            color="Country",
            hover_data=["Stock_Index"],
        )
        divs["scatter_cap_vs_index"] = _plot_div(fig)

    if {"Country", "Stock_Index", "Market_Cap_Trillion_USD"}.issubset(fdf.columns):
        fig = px.treemap(
            fdf,
            path=["Country", "Stock_Index"],
            values="Market_Cap_Trillion_USD",
            color="Market_Cap_Trillion_USD",
            color_continuous_scale="Blues",
        )
        divs["treemap_cap"] = _plot_div(fig)

    if {"Index_Value"}.issubset(fdf.columns):
        fig = px.box(fdf, y="Index_Value", points="suspectedoutliers")
        divs["box_index_value"] = _plot_div(fig)

    equity_cols = [c for c in ["Index_Value", "Daily_Change_Percent", "Market_Cap_Trillion_USD", "Commodity_Index", "Bond_Yield_10Y_Percent"] if c in fdf.columns]
    if len(equity_cols) >= 2:
        corr = fdf[equity_cols].corr(numeric_only=True)
        fig = ff.create_annotated_heatmap(z=corr.values.round(2), x=equity_cols, y=equity_cols, colorscale="RdBu", showscale=True, reversescale=True)
        divs["heatmap_corr"] = _plot_div(fig)

    return render_template("equity_markets.html", meta=meta, selected={"countries": countries, "ratings": ratings, "indices": indices, "start_date": request.args.get("start_date"), "end_date": request.args.get("end_date")}, **divs)


@app.route("/macro-and-rates")
def macro_and_rates():
    df = load_data(DATA_PATH)
    meta = get_distinct_values(df)
    countries, ratings, date_filter = _get_query_params(meta)
    fdf = apply_common_filters(df, countries, ratings, date_filter)

    divs = {"bar_gdp": None, "bar_infl": None, "bar_policy": None, "box_unemp": None, "scatter_infl_gdp": None, "scatter_policy_yield": None}

    if {"Country", "GDP_Growth_Rate_Percent"}.issubset(fdf.columns):
        fig = px.bar(
            fdf.sort_values("GDP_Growth_Rate_Percent", ascending=False), x="Country", y="GDP_Growth_Rate_Percent", color="GDP_Growth_Rate_Percent", color_continuous_scale="Greens"
        )
        divs["bar_gdp"] = _plot_div(fig)

    if {"Country", "Inflation_Rate_Percent"}.issubset(fdf.columns):
        fig = px.bar(
            fdf.sort_values("Inflation_Rate_Percent", ascending=False), x="Country", y="Inflation_Rate_Percent", color="Inflation_Rate_Percent", color_continuous_scale="OrRd"
        )
        divs["bar_infl"] = _plot_div(fig)

    if {"Country", "Interest_Rate_Percent"}.issubset(fdf.columns):
        fig = px.bar(
            fdf.sort_values("Interest_Rate_Percent", ascending=False), x="Country", y="Interest_Rate_Percent", color="Interest_Rate_Percent", color_continuous_scale="PuBu"
        )
        divs["bar_policy"] = _plot_div(fig)

    if {"Unemployment_Rate_Percent"}.issubset(fdf.columns):
        fig = px.box(fdf, y="Unemployment_Rate_Percent", points="suspectedoutliers")
        divs["box_unemp"] = _plot_div(fig)

    if {"Inflation_Rate_Percent", "GDP_Growth_Rate_Percent", "Country"}.issubset(fdf.columns):
        fig = px.scatter(fdf, x="Inflation_Rate_Percent", y="GDP_Growth_Rate_Percent", color="Country", trendline="ols")
        divs["scatter_infl_gdp"] = _plot_div(fig)

    if {"Interest_Rate_Percent", "Bond_Yield_10Y_Percent", "Country"}.issubset(fdf.columns):
        fig = px.scatter(fdf, x="Interest_Rate_Percent", y="Bond_Yield_10Y_Percent", color="Country")
        divs["scatter_policy_yield"] = _plot_div(fig)

    return render_template("macro_and_rates.html", meta=meta, selected={"countries": countries, "ratings": ratings, "start_date": request.args.get("start_date"), "end_date": request.args.get("end_date")}, **divs)


@app.route("/fx-and-commodities")
def fx_and_commodities():
    df = load_data(DATA_PATH)
    meta = get_distinct_values(df)
    countries, ratings, date_filter = _get_query_params(meta)
    currencies = request.args.getlist("currency") or meta.get("currencies", [])
    fdf = apply_common_filters(df, countries, ratings, date_filter)
    if currencies:
        fdf = fdf[fdf["Currency_Code"].isin(currencies)]

    divs = {"bar_fx_level": None, "bar_fx_ytd": None, "scatter_oil": None, "violin_gold": None, "heatmap_fx": None, "scatter_comm_infl": None}

    if {"Country", "Currency_Code", "Exchange_Rate_USD"}.issubset(fdf.columns):
        fig = px.bar(fdf.sort_values("Exchange_Rate_USD", ascending=False), x="Currency_Code", y="Exchange_Rate_USD", color="Country")
        divs["bar_fx_level"] = _plot_div(fig)

    if {"Currency_Code", "Currency_Change_YTD_Percent"}.issubset(fdf.columns):
        fig = px.bar(
            fdf,
            x="Currency_Code",
            y="Currency_Change_YTD_Percent",
            color=(fdf["Currency_Change_YTD_Percent"] >= 0).map({True: "Up", False: "Down"}),
            color_discrete_map={"Up": "#2ca02c", "Down": "#d62728"},
        )
        divs["bar_fx_ytd"] = _plot_div(fig)

    if {"Oil_Price_USD_Barrel", "Commodity_Index", "Country"}.issubset(fdf.columns):
        fig = px.scatter(fdf, x="Commodity_Index", y="Oil_Price_USD_Barrel", color="Country")
        divs["scatter_oil"] = _plot_div(fig)

    if {"Gold_Price_USD_Ounce", "Country"}.issubset(fdf.columns):
        fig = px.violin(fdf, y="Gold_Price_USD_Ounce", color="Country", box=True, points=False)
        divs["violin_gold"] = _plot_div(fig)

    cols = [c for c in ["Exchange_Rate_USD", "Currency_Change_YTD_Percent"] if c in fdf.columns]
    if len(cols) == 2:
        corr = fdf[cols].corr(numeric_only=True)
        fig = ff.create_annotated_heatmap(z=corr.values.round(2), x=cols, y=cols, colorscale="Blues", showscale=True)
        divs["heatmap_fx"] = _plot_div(fig)

    if {"Commodity_Index", "Inflation_Rate_Percent", "Country"}.issubset(fdf.columns):
        fig = px.scatter(fdf, x="Commodity_Index", y="Inflation_Rate_Percent", color="Country", trendline="ols")
        divs["scatter_comm_infl"] = _plot_div(fig)

    return render_template(
        "fx_and_commodities.html",
        meta=meta,
        selected={"countries": countries, "ratings": ratings, "currencies": currencies, "start_date": request.args.get("start_date"), "end_date": request.args.get("end_date")},
        **divs,
    )


@app.route("/prediction")
def prediction():
    # Country similarity recommendation (ported)
    df = load_data(DATA_PATH)
    if not {"Country", "Date"}.issubset(df.columns):
        return render_template("prediction.html", error="Country or Date column missing in data.")

    feature_cols = ["GDP_Growth_Rate_Percent", "Inflation_Rate_Percent"]
    if "Credit_Rating" in df.columns:
        credit_ratings_sorted = sorted(df["Credit_Rating"].dropna().unique(), reverse=True)
        credit_map = {k: v for v, k in enumerate(credit_ratings_sorted)}
        df["Credit_Rating_Num"] = df["Credit_Rating"].map(credit_map)
        feature_cols.append("Credit_Rating_Num")
    else:
        df["Credit_Rating_Num"] = 0
        feature_cols.append("Credit_Rating_Num")

    latest_df = df.sort_values("Date").groupby("Country").tail(1).reset_index(drop=True)
    country = request.args.get("country") or (latest_df["Country"].iloc[0] if len(latest_df) else None)

    recs_table_html = None
    if country:
        from sklearn.preprocessing import MinMaxScaler
        from sklearn.metrics.pairwise import cosine_similarity

        selected = latest_df[latest_df["Country"] == country][feature_cols].values
        scaler = MinMaxScaler()
        features_scaled = scaler.fit_transform(latest_df[feature_cols])
        sim = cosine_similarity(selected, features_scaled)[0]
        latest_df = latest_df.copy()
        latest_df["Similarity"] = sim
        recs = latest_df[latest_df["Country"] != country].sort_values("Similarity", ascending=False).head(5)
        recs_table_html = recs[["Country", "GDP_Growth_Rate_Percent", "Inflation_Rate_Percent", "Credit_Rating", "Similarity"]].to_html(
            classes="table table-sm table-striped", index=False, float_format=lambda x: f"{x:.2f}" if isinstance(x, float) else x
        )

    return render_template("prediction.html", countries=sorted(latest_df["Country"].unique().tolist()), selected_country=country, recs_table_html=recs_table_html)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)


