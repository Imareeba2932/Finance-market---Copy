## Global Finance Dashboard (Streamlit + Plotly)

Multi-page Streamlit app analyzing global markets with 30+ interactive charts.

### Features
- Home overview with KPIs and quick insights
- 5 analysis pages (Equity, Macro & Rates, FX & Commodities, Fixed Income & Credit, Trade & Real Estate)
- Per-page sidebar filters (country, credit rating, date, plus page-specific filters)
- Fast loading with caching, clean Plotly visuals

### Project Structure
```
Home.py
pages/
  1_Equity_Markets.py
  2_Macro_and_Rates.py
  3_FX_and_Commodities.py
  4_Fixed_Income_and_Credit.py
  5_Trade_and_Real_Estate.py
utils/
  data.py
Global finance data.csv
requirements.txt
```

### Setup
1) Create and activate a virtual environment (optional but recommended).

2) Install dependencies:
```bash
pip install -r requirements.txt
```

3) Run the app from the project directory:
```bash
streamlit run Home.py
```

If your default browser doesn't open, copy the local URL into your browser.

### Notes
- The app expects the CSV file `Global finance data.csv` in the project root.
- Date filters will appear automatically if the `Date` column is present.



