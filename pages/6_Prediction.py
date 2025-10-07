import streamlit as st
import pandas as pd
from utils.data import load_data
from pathlib import Path
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics.pairwise import cosine_similarity

st.set_page_config(page_title="Country Recommendation", page_icon="🌍")

st.title("Country Similarity Recommendation System")

st.markdown("""
> **Disclaimer:**
> 
> Only those countries appear in the selectbox which have the latest (most recent) entry with complete data for GDP Growth, Inflation, and Credit Rating. If a country is missing or has incomplete data in these columns, it will not be shown here. The recommendation system works based on the latest available financial values for each country.
""")

DATA_PATH = str(Path(__file__).parents[1] / "Global finance data.csv")
df = load_data(DATA_PATH)

st.write("Select a country to see which other countries are most similar based on GDP Growth, Inflation, and Credit Rating.")

# Prepare features for similarity
feature_cols = ["GDP_Growth_Rate_Percent", "Inflation_Rate_Percent"]
# Convert credit rating to numeric for similarity
if "Credit_Rating" in df.columns:
    credit_ratings_sorted = sorted(df["Credit_Rating"].dropna().unique(), reverse=True)
    credit_map = {k: v for v, k in enumerate(credit_ratings_sorted)}
    df["Credit_Rating_Num"] = df["Credit_Rating"].map(credit_map)
    feature_cols.append("Credit_Rating_Num")
else:
    df["Credit_Rating_Num"] = 0
    feature_cols.append("Credit_Rating_Num")

# Use only last available row per country
if "Country" in df.columns and "Date" in df.columns:
    latest_df = df.sort_values("Date").groupby("Country").tail(1).reset_index(drop=True)
else:
    st.error("Country or Date column missing in data.")
    st.stop()

country = st.selectbox("Country", latest_df["Country"].unique())

if country:
    selected = latest_df[latest_df["Country"] == country][feature_cols].values
    scaler = MinMaxScaler()
    features_scaled = scaler.fit_transform(latest_df[feature_cols])
    sim = cosine_similarity(selected, features_scaled)[0]
    latest_df["Similarity"] = sim
    recs = latest_df[latest_df["Country"] != country].sort_values("Similarity", ascending=False).head(5)
    st.subheader(f"Top 5 Similar Countries to {country}")
    st.table(recs[["Country", "GDP_Growth_Rate_Percent", "Inflation_Rate_Percent", "Credit_Rating", "Similarity"]].style.format({"Similarity": "{:.2f}"}))
    st.info("Similarity is calculated using GDP growth, inflation, and credit rating.")
else:
    st.warning("No country selected.")
